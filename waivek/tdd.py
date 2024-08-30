
def get_pairs(pairs_type):
    if pairs_type == bytes:
        pairs = [ ("nothing", None), ("binary", "Hello, World!".encode("utf-8") ), ("string", "b") ]
    elif pairs_type == list:
        numbers = list(range(10))
        pairs = [ ("nothing", None), ("numbers", numbers ), ("empty", None) ]
    return pairs

def test_ic_custom_types():

    from waivek.db import db_init, insert_dictionaries, get_schema
    from waivek.ic import ic
    connection = db_init("db_test/lists.db")
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS pairs;")

    pairs = get_pairs(list)

    dictionaries = [ { "key": key, "value": value } for key, value in pairs ]
    # cursor.execute("CREATE TABLE pairs ([key] TEXT, value LIST);")
    insert_dictionaries(cursor, "pairs", dictionaries)
    # cursor.executemany("INSERT INTO pairs ([key], value) VALUES (:key, :value);", dictionaries)
    connection.commit()
    dictionaries = [ { "key": key, "key_type": type(key), "value": value, "key_value": type(value) } for key, value in cursor.execute("SELECT key, value FROM pairs;") ]
    ic(dictionaries)
    print(f"CREATE TABLE pairs ({get_schema(cursor, 'pairs').column_definitions()});")

