
from common import rel2abs, print_red_line, make_string_green, truncate, Timer
import sqlite3
import json
from enum import IntEnum
timer = Timer()

def table_exists(cursor, table_name):
    statement = f"SELECT * FROM sqlite_master WHERE type='table' AND name='{table_name}'"
    D = cursor.execute(statement).fetchall()
    return True if D else False

def flatten(unflattened_list):
    from functools import reduce
    return reduce(lambda a,b:a+b, unflattened_list)

def db_init(db_path):
    db_path = rel2abs(db_path)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    return cursor, connection

def jsonify_lists(D):
    list_keys = [ key for key, value in D.items() if type(value) == list ]
    for key in list_keys:
        L = D[key]
        D[key] = json.dumps(L)
    return D

# flatten_dict({ "vim": "god", "css": "okay" }, "skills")
#     ->
# [ ("skills.vim", "god"), ("skills.css", "okay") ]
def flatten_dict(D, parent_keys=[]):
    pairs = []
    for k, v in D.items():
        if type(v) == dict:
            pairs = pairs + flatten_dict(v, parent_keys+[k])
        else:
            new_k = ".".join(parent_keys+[k])
            pairs.append((new_k, v))
    return pairs


def prepare_dict(D):
    pairs = flatten_dict(D)        # 1.10, 60%
    D = { k: v for k, v in pairs } # 0.26, 15%
    D = jsonify_lists(D)           # 0.45, 25%
    return D


def escape_key_if_required(key):
    if "." in key:
        key = f'"{key}"'
    return key

def escaped_keys(input_keys):
    keys = [ escape_key_if_required(key) for key in input_keys ]
    return keys

class SqliteType(IntEnum):
    TEXT = 1
    REAL = 2
    INTEGER = 3

    def from_text(arg):
        D = { "TEXT": SqliteType.TEXT, "REAL": SqliteType.REAL, "INTEGER": SqliteType.INTEGER }
        return D[arg]

def as_column_str(x):
    D = { str             : "TEXT", float           : "REAL", int                : "INTEGER", type(None) : "TEXT", bool: "INTEGER",
          SqliteType.TEXT : "TEXT", SqliteType.REAL : "REAL", SqliteType.INTEGER : "INTEGER" }
    if x not in D.keys():
        x = type(x)
    return D[x]

class Schema:
    "TEXT (null)"
    "TEXT (genuine)"
    "INTEGER"
    "REAL"

    def __init__(self, arg=None):
        if arg == [] or arg == None:
            self.D = {}
        else:
            items = arg if type(arg) == list else [ arg ]
            is_pragma = type(items[0]) == sqlite3.Row
            if is_pragma:
                self.D = { row_D["name"] : SqliteType.from_text(row_D["type"]) for row_D in items }
            else:
                self.D = self.dictionaries_to_schema(items)

    def dictionaries_to_schema(self, dictionaries):
        # items = flatten(list(D.items()) for D in dictionaries)
        items = []
        for D in dictionaries:
            for T in D.items():
                items.append(T)

        # timer.start("Implementation 1")
        # D1 = {}
        # content_offset_count = 0
        # for k, v in items:
        #     v1 = D1.get(k, SqliteType.TEXT) # 0.8, v1            = SqliteType.TEXT, INTEGER, REAL
        #     column_str = as_column_str(v)         # 2.3, as_column_str = "TEXT, "INTEGER", "REAL"
        #     v2 = SqliteType.from_text(column_str) # 3.7, v2            = SqliteType.TEXT, INTEGER, REAL
        #     D1[k] = max(v1, v2)             # 0.8, D1[k]   = SqliteType.TEXT, INTEGER, REAL
        #     if k == "content_offset_seconds":
        #         content_offset_count = content_offset_count + 1
        #         # if content_offset_count < 20:
        #         if v2 == 3:
        #             print(f"[{content_offset_count}] content_offset_seconds: {v}, v1: {v1}, v2: {v2}")
        # timer.print("Implementation 1")

        finalized_column_names = []
        type2sqlite = { type(None): SqliteType.TEXT, str: SqliteType.TEXT, float: SqliteType.REAL, int: SqliteType.INTEGER, bool: SqliteType.INTEGER }
        schema_D = {}
        for column_name, value in items:
            if column_name in finalized_column_names:
                continue
            value_type = type(value)
            schema_D[column_name] = type2sqlite[value_type]
            if value != None and value_type != int:
                finalized_column_names.append(column_name)

        return schema_D

    def join(self, with_types=False):
        if not with_types:
            return ", ".join(escaped_keys(self.keys()))
        return ", ".join(escape_key_if_required(key)+" "+as_column_str(value) for key, value in self.items())

    def column_definitions(self, constraint_D={}):
        # https://www.sqlite.org/syntax/column-constraint.html
        column_definitions = []
        for key, value in self.items():
            column_L = [ escape_key_if_required(key), as_column_str(value) ] 
            if constraint_D.get(key):
                column_L = [ escape_key_if_required(key), as_column_str(value), constraint_D.get(key)]
            else:
                column_L = [ escape_key_if_required(key), as_column_str(value) ]
            column_definition = " ".join(column_L)
            column_definitions.append(column_definition)
        return ", ".join(column_definitions)

    def keys(self):
        return self.D.keys()
    def values(self):
        return self.D.values()
    def items(self):
        return self.D.items()
    def get(self, key):
        return self.D.get(key)
    def __getitem__(self, key):
        return self.D[key]
    def __setitem__(self, key, value):
        self.D[key] = value
    def __len__(self):
        return len(self.D)
    def __repr__(self):
        return repr(self.D)
    def __eq__(self, rhs_schema):
        return self.D == rhs_schema.D


    def __str__(self):
        if len(self.D) == 0:
            return "Empty Schema"
        max_length = max(len(key) for key in self.D.keys())
        column_gap = 2
        separator = " " * column_gap
        gutter_length = 2
        gutter_string = " " * gutter_length
        lines = []
        for k, v in self.D.items():
            key_string = str(k).ljust(max_length)
            value_string = str(v)
            lines.append(gutter_string + key_string + separator + value_string)
        lines = [ "" ] + lines + [ "" ]
        return "\n".join(lines)


def get_schema(cursor, table_name):
    schema_query = cursor.execute(f"PRAGMA table_info('{table_name}');")
    rows = cursor.fetchall()
    schema = Schema(rows)
    return schema

def batch_execute(cursor, statements, print_statements=True):
    for statement in statements:
        cursor.execute(statement)
        if print_statements:
            print(statement)
            print()


def add_new_columns(cursor, table_name, dictionary_schema):
    table_schema = get_schema(cursor, table_name)
    new_columns_schema = Schema()
    new_columns_schema.D = { k: v for k, v in dictionary_schema.items() if table_schema.get(k) == None }
    new_column_statements = [ f"ALTER TABLE {table_name} ADD COLUMN {escape_key_if_required(k)} {as_column_str(v)};" for k, v in new_columns_schema.items() ]
    return new_column_statements

def modify_existing_column_types(cursor, table_name, dictionary_schema, constraint_D={}):
    def get_random_four_digit_hex():
        from random import randint
        min_hex = 4096
        max_hex = 65535
        return hex(randint(min_hex, max_hex))[2:]
    # We don’t check if table_schema has a key in dictionary_schema as this is meant to be run AFTER add_new_columns
    # There should be no key in dictionary that is not there in the table schema
    table_schema = get_schema(cursor, table_name)

    changed_columns = [ key for key in dictionary_schema.keys() if table_schema[key] != dictionary_schema[key] ]
    if len(changed_columns) == 0:
        return []

    for key in dictionary_schema.keys():
        table_schema[key] = max(dictionary_schema[key], table_schema[key])

    temp_table_name        = f"tmp_{table_name}_{get_random_four_digit_hex()}"
    create_table_statement = f"CREATE TABLE {temp_table_name} ({table_schema.column_definitions(constraint_D=constraint_D)});"
    key_string             = table_schema.join()
    insert_statement       = f"INSERT INTO {temp_table_name}({key_string}) SELECT {key_string} FROM {table_name};"
    drop_statement         = f"DROP TABLE {table_name};"
    rename_statement       = f"ALTER TABLE {temp_table_name} RENAME TO {table_name};"

    return [ create_table_statement, insert_statement, drop_statement, rename_statement ]

def get_insert_pair_with_on_conflict_clause(D, table_name):
    keys = D.keys()
    values = tuple(D[key] for key in keys)
    keys = escaped_keys(keys)
    column_name_string = ", ".join(keys)
    question_mark_string = ", ".join(["?"] * len(keys))
    prefixed_keys = [ f"excluded.{key}" for key in keys ]
    prefixed_column_name_string = ", ".join(prefixed_keys)
    statement = f"""
INSERT INTO {table_name} ({column_name_string}) VALUES ({question_mark_string})
ON CONFLICT DO UPDATE SET ({column_name_string})=({prefixed_column_name_string});
    """.strip()
    return (statement, values)

# TRIGGER
def get_create_trigger_statement(cursor, table_name, trigger_name, vcs_table_name, date_column_name="vcs_date_epoch_utc_seconds"):
    def get_primary_key(cursor, table_name):
        schema_query = cursor.execute(f"SELECT name FROM pragma_table_info('{table_name}') WHERE pk=1;")
        row = cursor.fetchone()
        primary_key = row["name"]
        return primary_key

    primary_key       = get_primary_key(cursor, table_name)
    table_schema      = get_schema(cursor, table_name)
    unescaped_column_names      = table_schema.keys()
    clauses           = []
    column_names      = []
    column_operations = []
    for unescaped_column_name in unescaped_column_names:
        escaped_column_name = escape_key_if_required(unescaped_column_name)
        old_prefix          = "old."+escaped_column_name
        new_prefix          = "new."+escaped_column_name
        condition           = f"{old_prefix} IS NOT {new_prefix}"
        column_operation    = f"NULLIF({old_prefix}, {new_prefix})"
        if unescaped_column_name != primary_key and unescaped_column_name != date_column_name:
            clauses.append(condition)
            column_names.append(escaped_column_name)
            column_operations.append(column_operation)
        else:
            column_names.append(escaped_column_name)
            column_operations.append(old_prefix)
    if len(clauses) == 0:
        return ""
    condition_string = " OR ".join(clauses)
    column_name_string = ", ".join(column_names)
    column_operation_string = ", ".join(column_operations)
    create_trigger_statement = f"""
CREATE TRIGGER {trigger_name}
    BEFORE UPDATE
    ON {table_name}
    WHEN {condition_string}
BEGIN
    INSERT INTO {vcs_table_name} ({column_name_string}) VALUES (
        {column_operation_string}
    );
END;
    """.strip()
    if column_name_string == "":
        print_red_line(f"column_name_string is EMPTY")
        breakpoint()
    return create_trigger_statement

# TRIGGER
def check_if_trigger_exists(cursor, table_name, trigger_name):
    query = f"SELECT COUNT(*) trigger_count FROM sqlite_master WHERE type='trigger' AND tbl_name='{table_name}' AND name='{trigger_name}';"
    row = cursor.execute(query).fetchone()
    trigger_count = row["trigger_count"]
    return trigger_count > 0

# TRIGGER
def add_date_column(dictionaries):
    from time import time
    epoch_utc = int(time())
    date_column_name = "vcs_date_epoch_utc_seconds"
    for D in dictionaries:
        D[date_column_name] = epoch_utc
    return dictionaries

def insert_dictionaries(cursor, table_name, dictionaries, constraint_D={}):
    print_statements = False

    dictionaries = [ prepare_dict(D) for D in dictionaries ]
    dictionaries = add_date_column(dictionaries)
    dictionary_schema = Schema(dictionaries)

    table_schema = get_schema(cursor, table_name)
    table_does_not_exist = len(table_schema) == 0

    # 1. CREATE TABLE IF IT DOES NOT EXIST
    if table_does_not_exist:
        create_table_statement = f"CREATE TABLE {table_name} ({dictionary_schema.column_definitions(constraint_D=constraint_D)});"
        cursor.execute(create_table_statement)
        if print_statements:
            print(create_table_statement)

    # 2. ADD NEW COLUMNS
    add_column_statements = add_new_columns(cursor, table_name, dictionary_schema)
    batch_execute(cursor, add_column_statements, print_statements)

    # 3. MODIFY UPDATED COLUMN TYPES
    modify_column_statements = modify_existing_column_types(cursor, table_name, dictionary_schema, constraint_D=constraint_D)
    batch_execute(cursor, modify_column_statements, print_statements)

    # 4.1. SETUP VCS TABLE {{{
    vcs_print_statements = False
    vcs_table_name = f"{table_name}_vcs"
    vcs_table_schema = get_schema(cursor, vcs_table_name)
    vcs_table_does_not_exist = len(vcs_table_schema) == 0

    if vcs_table_does_not_exist:
        create_vcs_table_statement = f"CREATE TABLE {vcs_table_name} ({dictionary_schema.column_definitions()});"
        cursor.execute(create_vcs_table_statement)
        if vcs_print_statements:
            print(create_vcs_table_statement)
    vcs_add_column_statements = add_new_columns(cursor, vcs_table_name, dictionary_schema)
    batch_execute(cursor, vcs_add_column_statements, vcs_print_statements)
    vcs_modify_column_statements = modify_existing_column_types(cursor, vcs_table_name, dictionary_schema)
    batch_execute(cursor, vcs_modify_column_statements, vcs_print_statements)
    # }}}
    # 4.2. ADD VCS TRIGGER
    trigger_name = f"update_trigger_{table_name}_vcs"
    if len(vcs_add_column_statements) > 0 or len(vcs_modify_column_statements) > 0: # SNIPPET 1 for debug
        cursor.execute(f"DROP TRIGGER IF EXISTS {trigger_name}")
        if vcs_print_statements:
            print(f"DROP TRIGGER IF EXISTS {trigger_name}")
    trigger_exists = check_if_trigger_exists(cursor, table_name, trigger_name)
    if not trigger_exists:
        try:
            create_trigger_statement = get_create_trigger_statement(cursor, table_name, trigger_name, vcs_table_name)
        except Exception as e:
            error = e
            breakpoint()
        cursor.execute(create_trigger_statement)
        if vcs_print_statements:
            print(create_trigger_statement)

    # 5. INSERT
    for D in dictionaries:
        insert_statement, values = get_insert_pair_with_on_conflict_clause(D, table_name)
        cursor.execute(insert_statement, values )
        if print_statements:
            print(insert_statement, make_string_green(truncate(str(values), 200)))
            print()


