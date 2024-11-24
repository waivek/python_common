from typing import List, TYPE_CHECKING, Any, TypeVar, Generic

from box.timer import Timer
from box.ic import ib

if TYPE_CHECKING:
    from peewee import ModelSelect

timer = Timer()

def get_pagination(
    total_items: int,
    page: int = 1,
    size: int = 50
) -> dict:
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

def get_clusters(query: "ModelSelect", column: str) -> List[tuple]:
    from peewee import fn
    # Get the base query conditions
    base_query = query.model.select()
    
    # Copy conditions from original query except those involving the cluster column
    if query._where: # pyright: ignore[reportAttributeAccessIssue]
        # If it's a compound expression (AND)
        if hasattr(query._where, 'lhs') and hasattr(query._where, 'rhs'): # pyright: ignore[reportAttributeAccessIssue]
            # If it's a field comparison
            if hasattr(query._where.lhs, 'name'): # pyright: ignore[reportAttributeAccessIssue]
                field_name = query._where.lhs.name # pyright: ignore[reportAttributeAccessIssue]
                if field_name != column:
                    base_query = base_query.where(query._where) # pyright: ignore[reportAttributeAccessIssue]
            # If it's nested expressions
            else:
                if column not in str(query._where.lhs): # pyright: ignore[reportAttributeAccessIssue]
                    base_query = base_query.where(query._where.lhs) # pyright: ignore[reportAttributeAccessIssue]
        else:
            # Single condition
            if column not in str(query._where): # pyright: ignore[reportAttributeAccessIssue]
                base_query = base_query.where(query._where) # pyright: ignore[reportAttributeAccessIssue]
    
    assert query.model.id
    model_id = query.model.id
    
    final_query = (base_query
        .select(
            getattr(query.model, column),
            fn.COUNT(model_id).alias('count')
        )
        .group_by(getattr(query.model, column))
        .order_by(fn.COUNT(model_id).desc()))
    
    # Get the SQL (for debugging)
    sql, params = final_query.sql()
    print(f"SQL Query: {sql}")
    print(f"Parameters: {params}")
    
    return list(final_query.tuples())

# Test code
if __name__ == "__main__":
    from peewee import SqliteDatabase, Model, AutoField, CharField
    # Create a test database in memory
    db = SqliteDatabase(':memory:')

    class TestModel(Model):
        id = AutoField()
        name = CharField()
        category = CharField()
        
        class Meta:
            database = db

    # Set up the database
    db.connect()
    db.create_tables([TestModel])

    # Insert expanded test data
    test_data = [
        {'name': 'Item 1', 'category': 'A'},
        {'name': 'Item 2', 'category': 'A'},
        {'name': 'Item 3', 'category': 'B'},
        {'name': 'Item 4', 'category': 'B'},
        {'name': 'Item 5', 'category': 'C'},
        {'name': 'Item 6', 'category': 'C'},
        {'name': 'Item 7', 'category': 'D'},
        {'name': 'Item 8', 'category': 'D'},
        {'name': 'Other 1', 'category': 'A'},  # Non-matching name
        {'name': 'Other 2', 'category': 'B'},  # Non-matching name
    ]
    TestModel.insert_many(test_data, fields=[TestModel.name, TestModel.category]).execute()

    # Test 1: Basic clustering with name filter
    print("\nTest 1: Basic clustering with name filter")
    query = TestModel.select().where(TestModel.name.contains('Item'))
    clusters = get_clusters(query, 'category')
    print("Results when filtering by name:")
    print(clusters)

    # Test 2: Clustering with single category filter
    print("\nTest 2: Clustering with single category filter")
    query = TestModel.select().where(
        (TestModel.name.contains('Item')) & 
        (TestModel.category == 'A')
    )
    clusters = get_clusters(query, 'category')
    print("Results when filtering by name AND category 'A':")
    print(clusters)

    # Test 3: Clustering with IN filter
    print("\nTest 3: Clustering with IN filter")
    query = TestModel.select().where(
        (TestModel.name.contains('Item')) & 
        (TestModel.category.in_(['A', 'B'])) # type:ignore
    )
    clusters = get_clusters(query, 'category')
    print("Results when filtering by name AND categories IN ('A', 'B'):")
    print(clusters)

    # Test 4: Clustering with NOT IN filter
    print("\nTest 4: Clustering with NOT IN filter")
    query = TestModel.select().where(
        (TestModel.name.contains('Item')) & 
        (TestModel.category.not_in(['A', 'B'])) # type:ignore
    )
    clusters = get_clusters(query, 'category')
    print("Results when filtering by name AND categories NOT IN ('A', 'B'):")
    print(clusters)

