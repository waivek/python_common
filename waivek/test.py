# ./coc-enter.vim

# print("__package__: " + __package__)

from waivek.timer import Timer   # Single Use
timer = Timer()
timer.start("test.py")
from waivek.color import Code    # Multi-Use
from waivek.error import handler # Single Use
from waivek.ic import ic         # Multi-Use
import time

def function_call(item_1, key=[1, 2, 3], D={}):
    pass

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
    from waivek.db import db_init
    temp_directory = os.path.expandvars("%TEMP%")
    db_path = os.path.join(temp_directory, "database.db")
    connection = db_init(db_path)
    cursor = connection.cursor()
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
    from waivek.db import insert_dictionaries
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
    from waivek.error import print_error_information

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

def rich_movie():
    """Same as the table_movie.py but uses Live to update"""
    import time
    from contextlib import contextmanager

    from rich import box
    from rich.align import Align
    from rich.console import Console
    from rich.live import Live
    from rich.table import Table
    from rich.text import Text

    TABLE_DATA = [
        [
            "May 25, 1977",
            "Star Wars Ep. [b]IV[/]: [i]A New Hope",
            "$11,000,000",
            "$1,554,475",
            "$775,398,007",
        ],
        [
            "May 21, 1980",
            "Star Wars Ep. [b]V[/]: [i]The Empire Strikes Back",
            "$23,000,000",
            "$4,910,483",
            "$547,969,004",
        ],
        [
            "May 25, 1983",
            "Star Wars Ep. [b]VI[/b]: [i]Return of the Jedi",
            "$32,500,000",
            "$23,019,618",
            "$475,106,177",
        ],
        [
            "May 19, 1999",
            "Star Wars Ep. [b]I[/b]: [i]The phantom Menace",
            "$115,000,000",
            "$64,810,870",
            "$1,027,044,677",
        ],
        [
            "May 16, 2002",
            "Star Wars Ep. [b]II[/b]: [i]Attack of the Clones",
            "$115,000,000",
            "$80,027,814",
            "$656,695,615",
        ],
        [
            "May 19, 2005",
            "Star Wars Ep. [b]III[/b]: [i]Revenge of the Sith",
            "$115,500,000",
            "$380,270,577",
            "$848,998,877",
        ],
    ]

    console = Console()

    BEAT_TIME = 0.04


    @contextmanager
    def beat(length: int = 1) -> None:
        yield
        time.sleep(length * BEAT_TIME)


    table = Table(show_footer=False)
    table_centered = Align.center(table)

    console.clear()

    with Live(table_centered, console=console, screen=False, refresh_per_second=20):
        with beat(10):
            table.add_column("Release Date", no_wrap=True)

        with beat(10):
            table.add_column("Title", Text.from_markup("[b]Total", justify="right"))

        with beat(10):
            table.add_column("Budget", "[u]$412,000,000", no_wrap=True)

        with beat(10):
            table.add_column("Opening Weekend", "[u]$577,703,455", no_wrap=True)

        with beat(10):
            table.add_column("Box Office", "[u]$4,331,212,357", no_wrap=True)

        with beat(10):
            table.title = "Star Wars Box Office"

        with beat(10):
            table.title = (
                "[not italic]:popcorn:[/] Star Wars Box Office [not italic]:popcorn:[/]"
            )

        with beat(10):
            table.caption = "Made with Rich"

        with beat(10):
            table.caption = "Made with [b]Rich[/b]"

        with beat(10):
            table.caption = "Made with [b magenta not dim]Rich[/]"

        for row in TABLE_DATA:
            with beat(10):
                table.add_row(*row)

        with beat(10):
            table.show_footer = True

        table_width = console.measure(table).maximum

        with beat(10):
            table.columns[2].justify = "right"

        with beat(10):
            table.columns[3].justify = "right"

        with beat(10):
            table.columns[4].justify = "right"

        with beat(10):
            table.columns[2].header_style = "bold red"

        with beat(10):
            table.columns[3].header_style = "bold green"

        with beat(10):
            table.columns[4].header_style = "bold blue"

        with beat(10):
            table.columns[2].style = "red"

        with beat(10):
            table.columns[3].style = "green"

        with beat(10):
            table.columns[4].style = "blue"

        with beat(10):
            table.columns[0].style = "cyan"
            table.columns[0].header_style = "bold cyan"

        with beat(10):
            table.columns[1].style = "magenta"
            table.columns[1].header_style = "bold magenta"

        with beat(10):
            table.columns[2].footer_style = "bright_red"

        with beat(10):
            table.columns[3].footer_style = "bright_green"

        with beat(10):
            table.columns[4].footer_style = "bright_blue"

        with beat(10):
            table.row_styles = ["none", "dim"]

        with beat(10):
            table.border_style = "bright_yellow"

        for box_style in [
            box.SQUARE,
            box.MINIMAL,
            box.SIMPLE,
            box.SIMPLE_HEAD,
        ]:
            with beat(10):
                table.box = box_style

        with beat(10):
            table.pad_edge = False

        original_width = console.measure(table).maximum

        for width in range(original_width, console.width, 2):
            with beat(1):
                table.width = width

        for width in range(console.width, original_width, -2):
            with beat(1):
                table.width = width

        for width in range(original_width, 90, -2):
            with beat(1):
                table.width = width

        for width in range(90, original_width + 1, 2):
            with beat(1):
                table.width = width

        with beat(2):
            table.width = None

def ic_test():
    for i in range(1, 5):
        hundred = i * 20
        L = list(range(0, hundred))
        # print("---")
        # print()
        # print(L)
        # ic(L)
        # print()

def make_short(filename):
    D = { 
            r"C:\Users\vivek\AppData\Roaming\Python\Python310\site-packages": "site-packages",
            r"C:\Users\vivek\Documents\Python": "common",
            r"C:\Program Files\Python310\lib": "builtin",
    }
    for string, replacement in D.items():
        filename = filename.replace(string, replacement)
    return filename

f = None
def tracefunc(frame, event, arg, indent=[0]):
    global f
    f = frame
    if event == "call":
        indent[0] += 2
        filename = frame.f_code.co_filename
        short_filename = make_short(filename)
        if indent == [0]:
            print()
        print(" " * indent[0] + "  call function", frame.f_code.co_name, short_filename)
    elif event == "return":
        print(" " + " " * indent[0], "exit function", frame.f_code.co_name)
        indent[0] -= 2
    return tracefunc

def trace_on():
    import sys
    sys.setprofile(tracefunc)

def f_string():
    number = 3.2
    value = f"{number}"
    print(value)

def m_list(obj):
    match obj:
        case [x]:
            string = f"One Item: {x}"
        case [_, 4, _]:
            string = "Contains 4"
        case [x, y]:
            string = f"Two Items: ({x}, {y})"
        case [*items]:
            string = f"Many Items: {items}"
    print(string)
        

    # if type(obj) == dict and 'data' in obj:
    #     # helix-global, helix-streamer
    #     dictionaries = obj['data']
    #     table = [ { 'name': D['name'], 'id': D['id'], 'api': 'helix' } for D in dictionaries ]
    #     return table
    # # case { 'channel_emotes': y, **kwargs }:
    # if type(obj) == dict and 'channelEmotes' in obj:
    #     # bttv-streamer
    #     dictionaries = obj['channelEmotes'] + obj['sharedEmotes']
    #     table = [ { 'name': D['code'], 'id': D['id'], 'api': 'bttv' } for D in dictionaries ]
    #     return table

def parse_emote_response(obj):
    if obj == []:
        # https://api.betterttv.net/3/cached/frankerfacez/users/twitch/59299632
        return []
    # case { 'data': y, **kwargs }:
    match obj:
        case { 'data': dictionaries }:
            # helix-global, helix-streamer
            table = [ { 'name': D['name'], 'id': D['id'], 'api': 'helix' } for D in dictionaries ]
            return table
        case { 'channelEmotes': [*L1], 'sharedEmotes': [*L2] }:
            # bttv-streamer
            dictionaries = L1 + L2
            table = [ { 'name': D['code'], 'id': D['id'], 'api': 'bttv' } for D in dictionaries ]
            return table

    dictionaries = obj
    match dictionaries[0]:
        case { 'id': _, 'code': _, 'user': _ }:
            # ffz-global, ffz-streamer
            table = [ { 'name': D['code'], 'id': D['id'], 'api': 'ffz' } for D in dictionaries ]
            return table
        case { 'id': _, 'code': _ }:
            # bttv-global
            table = [ { 'name': D['code'], 'id': D['id'], 'api': 'bttv' } for D in dictionaries ]
            return table
        case { 'id': _, 'name': _ }:
            # stv-global, stv-streamer
            table = [ { 'name': D['name'], 'id': D['id'], 'api': 'stv' } for D in dictionaries ]
            return table


def m_dict(obj):
    match obj:
        case { 'data': dictionaries }:
            string = dictionaries
        case { 'channelEmotes': [*L1], 'sharedEmotes': [*L2] }:
            string = L1 + L2

    dictionaries = obj
    # if D.get('id') and D.get('code') and D.get('user') is not None:
    match dictionaries[0]:
        case { 'id':_, 'code':_, 'user': _ }:
            # ffz-global, ffz-streamer
            table = [ { 'name': D['code'], 'id': D['id'], 'api': 'ffz' } for D in dictionaries ]
            return table

        # if D.get('id') and D.get('code') and D.get('user') is None:
        case { 'id':_, 'code':_ }:
            # bttv-global
            table = [ { 'name': D['code'], 'id': D['id'], 'api': 'bttv' } for D in dictionaries ]
            return table


        # if D.get('id') and D.get('name'):
        case { 'id': _, 'name': _ }:
            # stv-global, stv-streamer
            table = [ { 'name': D['name'], 'id': D['id'], 'api': 'stv' } for D in dictionaries ]
            return table
    print(string)
        
def test_bp():
    print("Breakpoint!")
    breakpoint()


def test_handler():
    [ 1/0 for i in range(5) ]

def test_partition():
    from waivek.common import create_partitions
    numbers = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ]
    pairs = create_partitions(len(numbers), 6)
    for start, end in pairs:
        list_slice = numbers[start:end]
        print(f"    {list_slice}")
    # end
    pass

def test_pathlib_ib():
    from pathlib import Path
    path = Path("C:/Users/file.txt")
    # ib(path)
    keys = [ key for key in dir(path) if not key.startswith("__") ]
    missing_attributes = []
    for key in keys:
        try:
            getattr(path, key)
        except Exception as e:
            missing_attributes.append(key)
    ic(missing_attributes)
    breakpoint()

def baz(string):
    return string.upper()

def bar(L):
    return ", ".join(str(item) for item in L)

def foo(x, y):
    return x+y

def rec(n):
    if n == 2:
        return
    return rec(n+1)

def test_trace():
    from waivek.trace import trace
    from waivek.trace import rerun
    trace([ "foo", "bar", "rec", "baz" ])
    ic(baz('latin'))
    ic(foo(1, 2))
    ic(bar(range(10)))
    ic(foo(3, 4))
    rec(0)
    rerun()

def get_frames():
    import sys
    import inspect
    inspect.stack()

    frames = []
    frame = sys._getframe()
    while frame:
        frames.append(frame)
        frame = frame.f_back
    ic(frames)

def test_sys():
    import sys
    L = [1, 2, 3]
    M = L + [ 4, 5, 6]
    print(sys.getrefcount(L))


# def dir():
#     from pathlib import Path
#     return Path(__file__).parent


def test_pathlib():
    timer.start("import os.path")
    import os.path; os.path
    t1 = timer.get("import os.path")
    timer.start("import Path")
    from pathlib import Path; Path
    t2 = timer.get("import Path")
    ic(t1, t2)
    from waivek.reltools import here
    path = here() / "f1/f2/item.txt"
    path.parent.mkdir(parents=True, exist_ok=True)


def test_os_path():
    import os.path
    path = "/Users/../vivek/"

    ic(path)
    ic(os.path.normpath(path))
    ic(os.path.abspath(path))


def test_static_variable():
    
    if 'call_count' not in dir(test_static_variable):
        test_static_variable.call_count = 0

    test_static_variable.call_count = test_static_variable.call_count + 1

def test_color_bash():
    result = """
    SELECT * FROM items
    """
    print("".join([Code.LIGHTGREEN_EX + "waivek@vivobook", ":", Code.LIGHTBLUE_EX + "/mnt/c/Users/vivek/Documents/Python"]))

def test_yield_list(): 

    def db_gen(query):
        from waivek.reltools import rel2abs
        from waivek.db import db_init
        path = rel2abs("./db_test/gen.db")
        connection = db_init(path)

        while True:
            cursor = connection.cursor()
            yield cursor.execute(query)

    query = "SELECT * FROM items;"
    result = db_gen(query)
    ic(result)


def test_datenames(): 
    from datetime import datetime, timedelta
    now = datetime.now()
    day_table = []
    for daynumber in range(7):
        d1 = now - timedelta(days=daynumber)
        d2 = now - timedelta(days=daynumber+1)
        end_epoch = int(d1.timestamp())
        start_epoch = int(d2.timestamp())
        if daynumber == 0:
            dayname = "today"
        elif daynumber == 1:
            dayname = "yesterday"
        else:
            dayname = f"{d1 :%a}".lower()
        day_table.append({ 'dayname': dayname, 'start_epoch': start_epoch, 'end_epoch': end_epoch })
    range_D = { 
         "day": now - timedelta(hours=24),
         "week": now - timedelta(days=7),
         "month": now - timedelta(days=30),
         "year": now - timedelta(days=365),
         "all": datetime(year=2005, month=1, day=1)
    }
    range_table = [ { "rangename": rangename, "start_epoch": int(dt.timestamp()), "end_epoch": int(now.timestamp()) } for rangename, dt in range_D.items() ]
    return { "range": range_table, "day": day_table }


def simulate(expression):
    import sys
    from waivek.frame import Frame
    frame = Frame(sys._getframe(1))
    start_line = frame.line.strip().replace("simulate(", "")[:-1]
    end_line = expression
    print(f">>> {start_line}")
    print(end_line)
    print()

def test_summaries():
    from waivek.common import Date
    from waivek.ic import ic; ic
    from datetime import datetime
    dt = datetime.now()
    year = dt.year
    date_string = f"{year}-01-01"
    date = Date(date_string)
    epoch = date.epoch
    epoch_string = f"Date({repr(date.epoch)})"
    str_string = f"Date({repr(date_string)})"
    strings = [epoch_string, str_string]
    # print("\n".join([ "date = " + string for string in  strings]))
    # ic(date.epoch)
    # ic(date.string)
    # ic(date.timeago())
    # ic(str(date))
    # ic(date.dt)

    # print()
    # print(">>> date.epoch")
    # print(f"{date.epoch}")
    # print()

    print(f">>> Date({repr(epoch)}) == Date({repr(date_string)})")
    print("True")
    print()
    print(f">>> date = Date({epoch})")
    simulate(date)
    simulate(date.epoch)
    simulate(date.string)
    simulate(date.timeago())
    simulate(str(date))
    simulate(date.dt)


def test_frame(a, b, c=1):
    timer.start("my-block-of-code")
    from waivek.frame import Frame
    frame = Frame(0)
    frame.print()
    timer.print("my-block-of-code")

def long_function():
    import time
    time.sleep(1)

def short_function():
    pass

def both_functions():
    test_frame(1, 2)
    long_function()
    short_function()


# Vim Command: NTF --- call s:PythonNewTestFunction()
def main():
    both_functions()
    return
    D = { 'a': 'A', 'b': 'B' }
    rich_movie()
    # test_frame(1,2, D)
    # test_yield_list()
    # test_color_bash()
    # test_static_variable()
    # test_os_path()
    # test_pathlib()
    # test_pudb()
    # test_sys()
    # ic({ "a": 100, "b": 1, "c": 100_000_000})
    # test_trace()
    # test_pathlib_ib()
    # m_list([1, 4])
    # m_dict({ 'a': 'b', 'data': 'match_data', 'c': 'd' })
    # m_dict({ 'a': 'b', 'channelEmotes': 'cemotes', 'sharedEmotes': ['semotes'], 'c': 'd' })

if __name__ == "__main__":
    with handler():
        main()

timer.print("test.py")
