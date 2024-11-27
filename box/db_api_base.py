from typing import List, Any, Tuple, TYPE_CHECKING
if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from sqlalchemy.sql.selectable import Select

def get_pagination(
    total_items: int,
    page: int = 1,
    size: int = 50
) -> dict:
    """Get pagination details.
    
    Args:
        total_items: Total number of items
        page: Current page number (1-based)
        size: Items per page
    
    Returns:
        Dictionary with pagination details
    """
    page = max(1, page)
    size = max(1, min(size, 100))
    total_pages = (total_items + size - 1) // size
    page = min(page, total_pages) if total_pages > 0 else 1
    
    return {
        'current_page': page,
        'page_size': size,
        'total_pages': total_pages,
        'is_first_page': page == 1,
        'is_last_page': page >= total_pages,
        'previous_page': page - 1 if page > 1 else None,
        'next_page': page + 1 if page < total_pages else None,
        'total_items': total_items
    }

def get_clusters_sqlalchemy(query: "Select", column: str, session: "Session") -> List[Tuple[Any, int]]:
    """
    A SQLAlchemy helper function.

    Takes a query and runs it. 

    If there is any WHERE clause in the query that filters for including / excluding the `column` or uses column `IN` or column `NOT IN`, thoses WHERE clauses should
    be removed before executing the query

    Then runs a GROUP BY on the results of the query.

    Returns that result.

    Basically provides an interface for creating buttons that user can press to add / remove tags

    Example:

    [
        { 'category': 'A', name: 'Apple' },
        { 'category': 'A', name: 'Astronaut' },
        { 'category': 'B', name: 'Banana' },
        { 'category': 'B', name: 'Bird' },
        { 'category': 'B', name: 'Bison' },
    ]

    CASE 1:
    if we run this table through the normal get_clusters, we should get:
    [
        { 'category': 'A', count: 2 },
        { 'category': 'B', count: 3 },
    ]
    
    CASE 2:
    if we run this table through the query:
    WHERE name == 'Apple', and cluster this via get_clusters, we should get:
    [
        { 'category': 'A', count: 1 },
    ]

    CASE 3:
    if we run this table through the query:
    WHERE category = 'A'
    the where clause should be removed and we should get:
    [
        { 'category': 'A', count: 2 },
        { 'category': 'B', count: 3 },
    ]

    CASE 4:
    if we run this table through the query:
    WHERE category IN ('A')
    the where clause should be removed and we should get:
    [
        { 'category': 'A', count: 2 },
        { 'category': 'B', count: 3 },
    ]
    as we don't want WHERE clauses that filter for including / excluding the `column` or uses column `IN` or column `NOT IN` to affect the clustering

    CASE 5:
    if we run this table through the query:
    WHERE category NOT IN ('A')
    the where clause should be removed and we should get:
    [
        { 'category': 'A', count: 2 },
        { 'category': 'B', count: 3 },
    ]

    """
    from sqlalchemy import select, func
    
    # Create a new select statement based on the original query
    modified_query = query
    
    # Remove WHERE clauses that filter on the specified column
    if hasattr(query, '_where_criteria') and query._where_criteria:
        new_criteria = []
        for criterion in query._where_criteria:
            # Skip criteria that involve the specified column
            if hasattr(criterion, 'left') and hasattr(criterion.left, 'name'):
                if criterion.left.name == column:
                    continue
                # Also skip IN/NOT IN clauses for the column
                if hasattr(criterion, 'operator') and criterion.operator.__name__ in ('in_op', 'notin_op'):
                    if criterion.left.name == column:
                        continue
            new_criteria.append(criterion)
        
        # Create new query with filtered WHERE clauses
        if len(new_criteria) != len(query._where_criteria):
            modified_query = select(*query.selected_columns)
            if new_criteria:
                modified_query = modified_query.where(*new_criteria)
    
    # Create a subquery once and reuse it
    subq = modified_query.subquery()
    
    # Create the grouping query using the same subquery reference
    group_query = (
        select(
            subq.c[column],
            func.count().label('count')
        )
        .select_from(subq)
        .group_by(subq.c[column])
        .order_by(subq.c[column])
    )
    
    # Execute and return results
    results = session.execute(group_query).all()
    return [(row[0], row[1]) for row in results]

# run.vim:vert term pytest tests/test_db_api_base.py
