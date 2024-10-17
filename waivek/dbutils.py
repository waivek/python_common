from waivek.timer import Timer
timer = Timer()

import os.path
import sys

def get_sqlite3():
    import typing   # takes 0.02s
    import sqlite3  # takes 0.02s
    import platform # takes 0.01s
    if platform.system() != "Linux":
        return sqlite3

    import pysqlite3
    return typing.cast(sqlite3, pysqlite3)

def get_connection(path: str):
    sqlite3 = get_sqlite3()
    connection = sqlite3.connect(path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON") # pragma foreign_keys=ON is needed for each connection
    return connection

def ensure_db_dir_exists(path):
    db_dir = os.path.dirname(path)
    if not os.path.exists(db_dir):
        raise Exception(f"Directory {db_dir} does not exist")

def to_absolute_path(path, caller_frame):
    if os.path.isabs(path):
        return path
    caller_path = str(caller_frame.f_globals.get('__file__'))
    caller_dir = os.path.dirname(caller_path)
    return os.path.join(caller_dir, path)

def Connection(path: str):
    if ":memory:" in path:
        return get_connection(path)

    caller_frame = sys._getframe(1)
    path = to_absolute_path(path, caller_frame)

    ensure_db_dir_exists(path)

    return get_connection(path)

# run.vim: vert term python waivek/__init__.py
