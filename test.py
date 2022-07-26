# ./coc-enter.vim
from timer import Timer   # Single Use
from color import Code    # Multi-Use
from error import handler # Single Use
from ic import ic         # Multi-Use
import time
timer = Timer()

def print_int(i):
    ic(Code.CYAN + i)

def print_list(L):
    five = 5
    zero = 0
    infinity = five / zero
    ic(Code.MAGENTA + L)

def print_str(s):
    ic(Code.GREEN + s)

def func(arg):
    if type(arg) == int:
        print_int(arg)
    elif type(arg) == list:
        print_list(arg)
    elif type(arg) == str:
        print_str(arg)

def caller():
    import sys
    import inspect
    stack = inspect.stack()
    frame2 = sys._getframe(1)


def git_is_dirty():
    import git
    path = r"C:\Users\vivek\Desktop\bkp\game"
    repo = git.Repo(path)
    index = False
    working_tree = False
    untracked_files = False
    submodules = False
    timer.start("is_dirty")
    ic(index, working_tree, untracked_files, submodules)
    breakpoint()
    is_dirty = repo.is_dirty(index=index, working_tree=working_tree, untracked_files=untracked_files, submodules=submodules, path='file-022.txt')
    ic(is_dirty)
    timer.print("is_dirty")
    time.sleep(1)

def sqlite_init():
    import os.path
    from db import db_init
    temp_directory = os.path.expandvars("%TEMP%")
    db_path = os.path.join(temp_directory, "database.db")
    cursor, connection = db_init(db_path)
    return cursor, connection

def sqlite_test():
    cursor, connection = sqlite_init()
    cursor.execute("DROP TABLE IF EXISTS pairs;")
    cursor.execute("CREATE TABLE IF NOT EXISTS pairs (key TEXT UNIQUE, value TEXT);")
    data = [ ("India", "New Delhi"), ("Japan" , "Tokyo"), ("USA", "Washington DC"), ("South Korea", "Seoul") ]
    cursor.executemany("INSERT INTO pairs (key, value) VALUES (?, ?);", data)
    # table = [ (key, value) for key, value in cursor.execute("SELECT key, value FROM pairs;").fetchall() ]
    table = [ key for key, in cursor.execute("SELECT key FROM pairs WHERE value != 'Tokyo';").fetchall() ]
    print(table)

def sqlite_test_2():
    cursor, connection = sqlite_init()
    cursor.execute("DROP TABLE IF EXISTS pairs;")
    cursor.execute("CREATE TABLE IF NOT EXISTS pairs (key TEXT UNIQUE ON CONFLICT REPLACE, value TEXT);")
    data = [ 
        ("condition_x", "True"), 
        ("condition_y", "True"), 
        ("condition_x", "False"), 
        ("condition_y", "False") 
    ]
    cursor.executemany("INSERT INTO pairs (key, value) VALUES (?, ?);", data)
    table = [ dict(row) for row in cursor.execute("SELECT * FROM pairs;").fetchall() ]
    ic(table)

def sqlite_test_3():
    cursor, connection = sqlite_init()
    cursor.execute("PRAGMA database_list")
    rows = [ dict(row) for row in cursor.fetchall() ]

def git_is_dirty_2():
    import git
    path = r"C:\Users\vivek\Desktop\bkp\scraper"
    repo = git.Repo(path)
    is_dirty = repo.is_dirty()
    breakpoint()
    ic(is_dirty)
    time.sleep(1)

def insert_dictionaries_test():
    from db import insert_dictionaries
    cursor, connection = sqlite_init()

    path = r"C:\Users\vivek\Desktop\bkp\game"
    status = "CLEAN"
    url = "https://github.com/waivek/bkp_game"
    order = 0

    cursor.execute("DROP TABLE IF EXISTS paths;")
    cursor.execute("CREATE TABLE paths (path TEXT UNIQUE, url TEXT, 'order' INTEGER, status TEXT);")
    insert_dictionaries(cursor, "paths", [ { "path": path, "url": url, "status": status } ])
    insert_dictionaries(cursor, "paths", [ { "path": path, "order": order } ])
    insert_dictionaries(cursor, "paths", [ { "path": path, "order": order + 1} ])
    connection.commit()
    rows = [ dict(row) for row in cursor.execute("SELECT * FROM paths;").fetchall() ]
    ic(rows)

from multiprocessing import Lock
from threading import Event
screen_lock = Lock()
threading_event = Event()
def lprint(string):
    global screen_lock
    # with screen_lock:
    print(string)


def print_string(string):
    for i in range(1000):
        print(f"[{i:02d}] {string} ")
        if string == "blue" and i == 3:
            message = f"Exception: string: {string}, i: {i}"
            raise Exception(message)
        time.sleep(1)


def start_many_threads():
    import threading
    colors = [ "red", "blue", "green", "yellow" ]
    thread_names = [ f"thread-{color}" for color in colors ]
    threads = [ threading.Thread(target=print_string, args=(color,), name=thread_name, daemon=False) for color, thread_name in zip(colors, thread_names) ]
    total = len(threads)
    for thread in threads:
        thread.start()
    while True:
        time.sleep(1)
        active_threads = [ thread for thread in threading.enumerate() if thread.name in thread_names ]
        count = len(active_threads)
        print(f"[start_many_threads] {count} / {total} alive")

def multiprocessing_multithreading_kill_test():
    from multiprocessing import Process
    from datetime import datetime
    from error import print_error_information

    p1 = Process(target=start_many_threads)
    try:
        p1.start()
        TIMEOUT = 10
        for i in range(TIMEOUT, 0, -1):
            now = datetime.now()
            print(f"[{now:%H:%M:%S}] [multiprocessing] Going to terminate in {i} seconds ")
            time.sleep(1)
    except BaseException as e:
        print_error_information(e)
    finally:
        p1.terminate()

def internet(host="8.8.8.8", port=53, timeout=3):
    # 0.03s - 0.06s
    import socket
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        return True

    except socket.error as ex:
        return False

def f_one():
    cursor, connection = sqlite_init()
    cursor.execute("DROP TABLE IF EXISTS pairs;")
    cursor.execute("CREATE TABLE IF NOT EXISTS pairs (key TEXT UNIQUE, value TEXT);")
    data = [ ("India", "New Delhi"), ("Japan" , "Tokyo"), ("USA", "Washington DC"), ("South Korea", "Seoul") ]
    cursor.executemany("INSERT INTO pairs (key, value) VALUES (?, ?);", data)
    # rows = [ dict(row) for row in cursor.execute("SELECT * FROM pairs;").fetchall() ]
    # ic(rows)
    row = cursor.execute("SELECT count(*) max_order FROM pairs;").fetchone()
    breakpoint()

def sqlite_select_test():
    import os
    path = r"C:\Users\vivek\Documents\Python\backup-flask\data_dev.db"
    os.system(f'cmd /k sqlite3 {path} -cmd "SELECT * FROM paths"')

def print_loop():
    from datetime import datetime
    index = 0
    while True:
        index = index + 1
        ds = Code.LIGHTBLACK_EX + f"{datetime.now():%Y-%m-%d %H:%M:%S} :"
        print(f"{ds} {index}")
        time.sleep(1)

def path_test():
    import os.path
    path = r"C:\Users\vivek\Documents\Python\backup-flask\data_dev.db"
    L = os.path.splitext(path)
    ic(L)

def ic_test():
    for i in range(1, 5):
        hundred = i * 100
        L = list(range(0, hundred))
        print("---")
        print()
        ic(L)
        print()


def main():
    from colorama import init
    init(convert=True)
    ic_test()

if __name__ == "__main__":
    with handler():
        main()
