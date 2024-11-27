import pytest
from sqlalchemy import Integer, Select, create_engine, select, Table, Column, String, MetaData
from sqlalchemy.orm import Query, Session, declarative_base
from rich import print as rprint
from rich.panel import Panel
from rich.table import Table as RichTable
from typing import Any

from box.db_api_base import get_clusters_sqlalchemy

import rich
console = rich.get_console()

def where_clause_to_str(query: Query | Select) -> str:
    # Convert SQLAlchemy query where clauses to readable SQL/English text. {{{
    """
    Convert SQLAlchemy query where clauses to readable SQL/English text.
    
    Args:
        query: SQLAlchemy query object
    
    Returns:
        str: Human-readable string representation of where clauses
    """
    # Extract where clauses from query
    whereclause = query._where_criteria
    if not whereclause:
        return "No where clauses"
        
    # Convert tuple to list
    whereclause = list(whereclause)
    
    def _process_binary_expression(expr):
        left = expr.left.name if hasattr(expr.left, 'name') else str(expr.left)
        right = expr.right.value if hasattr(expr.right, 'value') else str(expr.right)
        operator = expr.operator.__name__
        
        # Map common operators to readable text
        operator_map = {
            'eq': '=',
            'ne': '!=',
            'gt': '>',
            'lt': '<',
            'ge': '>=',
            'le': '<=',
            'like': 'LIKE',
            'ilike': 'ILIKE',
            'in_': 'IN',
            'in_op': 'IN',
            'notin_': 'NOT IN',
            'not_in_op': 'NOT IN',
        }
        
        op_str = operator_map.get(operator, operator)
        
        # Special handling for IN and NOT IN operators
        if op_str in ('IN', 'NOT IN'):
            if isinstance(right, list):
                formatted_values = f"({', '.join(repr(val) for val in right)})"
            else:
                formatted_values = f"({repr(right)})"
            return f"{left} {op_str} {formatted_values}"
            
        return f"{left} {op_str} {right}"
    
    def _process_clause(clause):
        if isinstance(clause, tuple):
            # Handle tuple of clauses
            return ' AND '.join(_process_clause(c) for c in clause)
        elif hasattr(clause, 'operator'):
            if hasattr(clause, 'clauses'):
                # Handle AND/OR conditions
                subclauses = [_process_clause(c) for c in clause.clauses]
                operator = ' AND ' if clause.operator.__name__ == 'and_' else ' OR '
                return f"({operator.join(subclauses)})"
            return _process_binary_expression(clause)
        return str(clause)
    
    # Process all clauses and join with AND
    processed_clauses = [_process_clause(clause) for clause in whereclause]
    result = ' AND '.join(processed_clauses) if len(processed_clauses) > 1 else processed_clauses[0]
    
    # Add WHERE prefix if there are where clauses
    return f"WHERE {result}" if whereclause else "No where clauses"
    # }}}

def print_test_results(name: str, query, results, raw_rows, input_table):
    """Pretty print test results using rich"""
    # Create panel for test case
    
    results_table = RichTable(show_header=False, box=None)
    
    results_table.add_row("[bold]Input Table", str(input_table))
    
    results_table.add_row("[bold]Query", query)
    results_table.add_row("[bold]Results", str(results))
    results_table.add_row("[bold]Raw Rows", str(raw_rows))
    
    panel = Panel(results_table, expand=False, title=f"\n[bold] {name} ", padding=1)
    print()
    console.print(panel)

@pytest.fixture
def test_table():
    # Create in-memory SQLite database and engine
    engine = create_engine('sqlite:///:memory:')
    
    # Create table definition
    metadata = MetaData()
    table = Table('test_table', metadata,
        Column('category', String),
        Column('name', String),
    )
    
    # Create the table in the database
    metadata.create_all(engine)
    
    # Create session and insert test data
    with Session(engine) as session:
        session.execute(table.insert(), [
            {'category': 'A', 'name': 'Apple'},
            {'category': 'A', 'name': 'Astronaut'},
            {'category': 'B', 'name': 'Banana'},
            {'category': 'B', 'name': 'Bird'},
            {'category': 'B', 'name': 'Bison'},
        ])
        session.commit()
        
        yield session, table

def test_case1_basic_grouping(test_table):
    session, table = test_table
    input_data = session.execute(select(table)).all()
    
    query = select(table.c.category, table.c.name).select_from(table)
    results = get_clusters_sqlalchemy(query, 'category', session)
    rows = session.execute(query).all()
    
    print_test_results("Basic Grouping Test", where_clause_to_str(query), results, rows, input_data)
    
    assert results == [
        ('A', 2),  # Category A has 2 items
        ('B', 3),  # Category B has 3 items
    ]

def test_case2_name_filter(test_table):
    session, table = test_table
    input_data = session.execute(select(table)).all()
    
    query = (
        select(table.c.category, table.c.name)
        .where(table.c.name == 'Apple')
    )
    
    results = get_clusters_sqlalchemy(query, 'category', session)
    rows = session.execute(query).all()
    
    print_test_results(
        "Case 2: Name Filter",
        where_clause_to_str(query),
        results,
        rows,
        input_data
    )
    
    assert results == [('A', 1)]

def test_case3_category_equals(test_table):
    session, table = test_table
    input_data = session.execute(select(table)).all()
    
    query = (
        select(table.c.category, table.c.name)
        .where(table.c.category == 'A')
    )
    
    results = get_clusters_sqlalchemy(query, 'category', session)
    rows = session.execute(query).all()
    
    print_test_results(
        "Case 3: Category Equals",
        where_clause_to_str(query),
        results,
        rows,
        input_data
    )
    
    assert results == [('A', 2), ('B', 3)]

def test_case4_category_in(test_table):
    session, table = test_table
    input_data = session.execute(select(table)).all()
    
    query = (
        select(table.c.category, table.c.name)
        .where(table.c.category.in_(['A']))
    )
    
    results = get_clusters_sqlalchemy(query, 'category', session)
    rows = session.execute(query).all()
    
    print_test_results(
        "Case 4: Category IN",
        where_clause_to_str(query),
        results,
        rows,
        input_data
    )
    
    assert results == [('A', 2), ('B', 3)]

def test_case5_category_not_in(test_table):
    session, table = test_table
    input_data = session.execute(select(table)).all()
    
    query = (
        select(table.c.category, table.c.name)
        .where(table.c.category.notin_(['A']))
    )
    
    results = get_clusters_sqlalchemy(query, 'category', session)
    rows = session.execute(query).all()
    
    print_test_results(
        "Case 5: Category NOT IN",
        where_clause_to_str(query),
        results,
        rows,
        input_data
    )
    
    assert results == [('A', 2), ('B', 3)]

# run.vim: term ++rows=100 pytest % -v -s
