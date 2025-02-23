from box import Timer
timer = Timer()
from box import handler, ic, ib , rel2abs

def insert_unique(connection, table_name: str, rows: list):
    cursor = connection.cursor()

    # create temp table in sqlite database
    temp_table_name = f"temp_{table_name}"
    cursor.execute(f"CREATE TEMP TABLE {temp_table_name} AS SELECT * FROM {table_name} WHERE 0")

    # insert rows into temp table
    cursor.executemany(f"INSERT INTO {temp_table_name} VALUES ({','.join(['?']*len(rows[0]))})", rows)

    # insert rows from temp table into main table
    cursor.execute(f"INSERT OR IGNORE INTO {table_name} SELECT * FROM {temp_table_name}")

def main():
    pass

if __name__ == "__main__":
    with handler():
        main()
