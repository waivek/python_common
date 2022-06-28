# commit-push [ tag auto-commits-on-change(5m window) ]
# daemon [ icon schedule watch ]
# import.py
# pipreqs.py

import sys

sys.path = [ "C:/users/vivek/Documents/Python/" ] + sys.path
from timer import Timer   # Single Use
timer = Timer()
from color import Code    # Multi-Use
from error import handler # Single Use
from ic import ib
from ic import ic # Multi-Use, import time: 70ms - 110ms
import git
from common import Date
import os.path
import time
import zmq
from loguru import logger

import threading
screen_lock = threading.Lock()
commit_lock = threading.Lock()
poll_rlock = threading.RLock()
db_lock = threading.Lock()
poll_event = threading.Event()
keyboard_event = threading.Event()
should_restart_watcher = False
is_overlap = False


def rel2abs(relative_path):
    frame            = sys._getframe(1)
    called_path      = frame.f_code.co_filename
    parent_directory = os.path.dirname(os.path.realpath(called_path))
    absolute_path    = os.path.realpath(os.path.join(parent_directory, relative_path))
    return absolute_path

def db_init(db_path):
    import platform
    if platform.system() == "Linux":
        import pysqlite3 as sqlite3
    else:
        import sqlite3
    connection = sqlite3.connect(db_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    return cursor, connection

def get_log_db_path():
    DB_PATH = rel2abs("backup-flask/logs.db")
    return DB_PATH

def get_data_db_path():
    DB_PATH = rel2abs("backup-flask/data.db")
    return DB_PATH

def sqlite_sink(message):
    global db_lock
    cu, connection = db_init(get_log_db_path())
    record = message.record

    # Contains __tracebac__, can be used for all exception handling use-cases
    error_object = record['exception'].value

    epoch = record['time'].timestamp()
    lvl_name = record['level'].name
    lvl = record['level'].no
    with db_lock:
        cursor.execute("CREATE TABLE IF NOT EXISTS errors (epoch REAL, lvl INTEGER, lvl_name TEXT, msg TEXT);")
        cursor.execute("INSERT INTO errors VALUES (?, ?, ?, ?);", (epoch, lvl, lvl_name, message))
        connection.commit()

format_string = '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <5}</level> | <level>{message}</level>'
log_out_file = rel2abs("backup-flask/log.txt")
logger.remove()
logger.add(sys.stdout, format=format_string)
logger.add(log_out_file, format=format_string, backtrace=True, diagnose=True)
logger.add(sqlite_sink, format=format_string, level="ERROR")

def print_safe(*args, end="\n"):
    s = " ".join([ str(arg) for arg in args ])
    global is_overlap
    if end == "\r":
        is_overlap = True
    global screen_lock
    with screen_lock:
        if is_overlap and end == "\n":
            is_overlap = False
            print()
        if end != "\r":
            logger.info(s)
        else:
            print(s, end=end)

def unused_silencer():
    Code, ic, ib

def is_git_repo(path):
    try:
        _ = git.Repo(path).git_dir
        return True
    except git.exc.InvalidGitRepositoryError:
        return False

def no_remote(repo):
    if True in [ref.is_remote() for ref in repo.references]:
        return False
    else:
        return True


def pipreqs(path):
    import shutil
    import subprocess
    if shutil.which("pipreqs") == None:
        print_safe(Code.RED + "Install and add pipreqs to $PATH. `pip install pipreqs`")
        return
    subprocess.run(['pipreqs', '--force', path])

# Edge cases:
#
#   1. Remote repo has changed and a pull + merge is required (this should be done by CLI not automatically, but detect and print this information)
#   2. Branches (only commit stuff on main branch? unsure), look into: repo.remotes.origin.push(refspec='master:master')
#   3. Adding files is not counted as a change. `requirements.txt` has to be manually added.
#   4. Make sure to not commit when user themselves is committing something manually.
def backup(path):
    # git init
    # git remote add origin https://github.com/waivek/autotest.git
    # git add .
    # git commit -m "first commit"
    # git push -u origin master

    start_time = time.time()
    from glob import glob
    exception = None

    try:
        if not is_git_repo(path):
            print_safe(Code.RED + f"No .git repostiory for {path}")
            return

        repo = git.Repo(path)

        if no_remote(repo):
            print_safe(Code.RED + f"No remote for .git repository {path}")
            return

        no_changes = repo.index.diff(None) == []

        requirements_path = os.path.join(path, "requirements.txt")
        if not os.path.exists(requirements_path) and len(glob("*.py")) > 0:
            pipreqs(path)
            repo.git.add(requirements_path)
            repo.git.commit('-m', '(auto-commit) requirements.txt')

        if no_changes:
            print_safe(f"[backup] No Changes, Exiting PATH='{path}'")
            return

        repo.git.commit('-am', '(auto-commit)')
        repo.remotes.origin.push()
        print_safe(f'[backup] Completed for PATH="{path}"')
    except Exception as e:
        exception = str(e)

    time_taken = time.time() - start_time
    return time_taken, exception



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

def check_if_main_thread():
    is_main_thread = threading.current_thread() == threading.main_thread()
    return is_main_thread


def server():
    # https://gist.github.com/gmolveau/10c80785d499c2e2d4c447343a624664
    from flask import Flask, render_template, jsonify, request
    import glob
    data_dir = get_data_db_path()
    cursor, connection = db_init(data_dir)
    poll_is_set = False

    root_folder = rel2abs('backup-flask')
    print_safe(Code.GREEN + "[server] " + root_folder)
    app = Flask(__name__, template_folder=root_folder, static_folder=root_folder)

    @app.route("/")
    def hello_world():
        import os
        rows = cursor.execute("SELECT path FROM paths").fetchall()
        paths = [ row['path'] for row in rows ]
        test_location = r"C:\Users\vivek\Desktop\bkp"

        test_folders = [ folder for folder in glob.glob(test_location + "/*") if os.path.isdir(folder) ]
        basenames = [ os.path.basename(folder) for folder in test_folders ]
        remotes = [ f"https://www.github.com/waivek/bkp-{basename}" for basename in basenames ]
        folder_payload = [ { "path": A, "basename": B, "remote": C} for A, B, C in zip(test_folders, basenames, remotes) ]
        has_internet = internet()
        # has_internet = True
        
        return render_template('gui.html', paths=paths, folder_payload=folder_payload, has_internet=has_internet)

    def autocomplete_path(path):
        from pathlib import Path
        # ~
        # Empty = C:
        # Partial Directory
        if path == "" or path == "C" or path == "C:" or path == "c" or path == "c:":
            path = "C:/"
        if '~' in path:
            path = os.path.expanduser(path)
        if not os.path.exists(path) and "/" not in path and "\\" not in path:
            return []
        path_glob = path + "*"
        suggestions =  [ path for path in glob.glob(path_glob) if os.path.isdir(path) and not os.path.islink(path) ]
        results = []
        for suggestion in suggestions:
            dirname, foldername = os.path.split(suggestion)
            dirname = Path(dirname).resolve()
            result = os.path.join(dirname, foldername)
            results.append(result)
        return results


    @app.route("/api/get_available_paths", methods=['POST'])
    def get_available_paths():
        D = request.json
        suggestions = autocomplete_path(D["input_value"])
        return jsonify(suggestions)

    @app.route("/api/db_add", methods=[ "PUT" ])
    def db_add():
        D = request.json
        path = D["path"]
        cursor.execute("REPLACE INTO paths VALUES (?);", (path,))
        connection.commit()

        start_time = time.time()
        zmq_client({"restart_watcher": True })
        time_taken = time.time() - start_time
        print_safe(f"GET zmq_client(): {time_taken:.2f} seconds")
        return "200"

    @app.route("/api/db_remove", methods=[ "DELETE" ])
    def db_remove():
        D = request.json
        path = D["path"]
        cursor.execute("DELETE FROM paths WHERE path=?;", (path,))
        connection.commit()
        zmq_client({"restart_watcher": True })
        return "200"

    def get_filepaths(directory):
        import re
        file_pattern = r"file-\d\d\d\.txt"
        glob_pattern = os.path.join(directory, "*")
        glob_results = glob.glob(glob_pattern)
        filepaths = [ path for path in glob_results if os.path.isfile(path) if re.match(file_pattern, os.path.basename(path)) ]
        return filepaths


    @app.route("/api/fileop_add", methods=[ "POST" ])
    def fileop_add():
        D = request.json
        directory = D["path"]
        filepaths = get_filepaths(directory)
        index = len(filepaths) + 1
        file_format = "file-{index:03d}.txt"
        filename = file_format.format(index=index)
        new_filepath = os.path.join(directory, filename)
        open(new_filepath, "w").close()

        dirname = os.path.basename(directory)
        filepath = os.path.join(dirname, filename).replace("\\", "/")
        return jsonify(f"add {filepath}"), 200

    @app.route("/api/fileop_modify", methods=["POST"])
    def fileop_modify():
        import random
        import dateutil.parser
        IST = dateutil.tz.gettz("Asia/Kolkata")
        from datetime import datetime
        D = request.json
        directory = D["path"]
        filepaths = get_filepaths(directory)
        if len(filepaths) == 0:
            return jsonify("Empty Directory, No File’s to Modify"), 200
        random_index = random.randrange(0, len(filepaths)-1, 1)
        random_filepath = filepaths[random_index]
        now = datetime.now().astimezone(IST)
        date_string = now.strftime("%a %b %e %H:%M:%S %Z %Y")
        line = f"[{date_string}]"
        with open(random_filepath, "a") as f:
            f.write(line + "\n")
        with open(random_filepath, "r") as f:
            lines = f.readlines()
            line_count = len(lines)
        # return jsonify({"random_filepath": random_filepath, "line_count": line_count }), 200
        dirname = os.path.basename(directory)
        filename = os.path.basename(random_filepath)
        filepath = os.path.join(dirname, filename).replace("\\", "/")
        return jsonify(f"mod {filepath}"), 200

    @app.route("/api/fileop_delete", methods=[ "POST" ])
    def fileop_delete():
        import os
        D = request.json
        directory = D["path"]
        filepaths = get_filepaths(directory)
        if len(filepaths) == 0:
            return jsonify("Empty Directory, No File’s to Delete"), 200
        filepaths.sort()
        last_filepath = filepaths[-1]
        os.remove(last_filepath)

        dirname = os.path.basename(directory)
        filename = os.path.basename(last_filepath)
        filepath = os.path.join(dirname, filename).replace("\\", "/")
        return jsonify(f"del {filepath}"), 200

    @app.route("/api/git_add", methods=["POST"])
    def git_add():
        D = request.json
        directory = D["path"]
        if not is_git_repo(directory) or no_remote(git.Repo(directory)):
            return "No .git repo / No remote. Exit.", 200
        repo = git.Repo(directory)
        file_git_wildcard = "file-*.txt"
        repo.index.add(file_git_wildcard) # Only for PATH, not actual code
        # repo.git.add(update=True)
        if repo.is_dirty():
            repo.git.commit('-am', f'(/api/git_add) Added {file_git_wildcard}')
            return jsonify(f"Added {file_git_wildcard}"), 200
        else:
            return jsonify("Nothing to add!"), 200

    @app.route("/poll", methods=["GET"])
    def poll():
        # global poll_event
        nonlocal poll_is_set
        global poll_rlock

        if not poll_rlock._is_owned():
            poll_rlock.acquire()

        log_dir = get_log_db_path()
        cursor, connection = db_init(log_dir)

        epoch = float(request.args.get("epoch"))
        # while not poll_event.is_set():
        #     poll_event.wait(0.1)
        # poll_event.clear()
        if epoch == 0:
            row = cursor.execute("SELECT epoch FROM backup;").fetchone()
            if row:
                rows = [ dict(row) for row in cursor.execute(f"SELECT * FROM backup WHERE epoch >= {epoch} ORDER BY epoch DESC;").fetchall() ]
                return jsonify(rows), 200

        poll_rlock.release()
        while not poll_is_set:
            time.sleep(0.1)
        poll_rlock.acquire()
        poll_is_set = False

        # cursor.execute("CREATE TABLE IF NOT EXISTS backup (date_string TEXT, epoch REAL time_taken, REAL, status TEXT, exception TEXT);")
        rows = [ dict(row) for row in cursor.execute(f"SELECT * FROM backup WHERE epoch >= {epoch} ORDER BY epoch DESC;").fetchall() ]

        D = {
            "backup_rows": rows,
            "dirty_directories": []
        }

        return jsonify(rows), 200
    
    @app.route("/set_poll")
    def set_poll():
        nonlocal poll_is_set
        poll_is_set = True
        return jsonify("Done"), 200


    def db():
        cursor.execute("CREATE TABLE IF NOT EXISTS paths (path TEXT UNIQUE);")
        connection.commit()

    context = zmq.Context()
    # print_safe("[zmq_client] Connecting to localhost:5555…")
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    def zmq_client(payload_D):
        nonlocal socket
        socket.send_json(payload_D)
        D = socket.recv_json()
        print_safe(D)

    db()
    is_main_thread = check_if_main_thread()
    app.run(host='0.0.0.0', use_reloader=is_main_thread, port=5000, debug=True, threaded=True)

def gui():
    
    filepath = 'http://localhost:5000'
    import subprocess, os, platform
    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
    else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))

def get_tracked_filepaths(path):
    if not is_git_repo(path):
        print_safe(Code.RED + f"No .git repostiory for {path}")
        print_safe(Code.RED + "This was triggered in the watcher, so .git corruption could have occurred.")
        return []
    # 200 ms, worth it so that we don’t have to deal with caching correctness
    repo = git.Repo(path)
    configFiles = repo.git.execute( ['git', 'ls-tree', '-r',  'master', '--name-only']).split()
    paths = [ os.path.normpath(os.path.join(path, file)) for file in configFiles ]
    return paths


def watch(path):

    from watchdog.events import FileSystemEventHandler
    class BackupHandler(FileSystemEventHandler):

        def __init__(self):
            self.last_valid_mod_time = 0
            self.unconsumed_events = []

        def log_event(self, D):
            self.unconsumed_events.append(D)

        def on_modified(self, event):
            abs_path = os.path.abspath(event.src_path)
            mod_time = time.time()

            abs_path = os.path.abspath(event.src_path)
            if os.path.exists(abs_path):
                not_vim_file = not abs_path.endswith("~")
                if not_vim_file:
                    mod_time = time.time()
                    seconds_elapsed = mod_time - self.last_valid_mod_time
                    if True or seconds_elapsed > 0.3:
                        tracked_filepaths = get_tracked_filepaths(path)
                        if abs_path in tracked_filepaths:
                            repo = git.Repo(path)
                            is_dirty = repo.is_dirty() # Takes 300ms
                            if is_dirty:
                                dt = Date(mod_time).dt.strftime("%b %d %H:%M:%S")
                                elapsed_string = f"+{seconds_elapsed:.1f}s".rjust(len("+000.0s"))
                                elapsed_string = Code.RED + elapsed_string if seconds_elapsed < 1 else Code.GREEN + elapsed_string
                                print(dt, elapsed_string, abs_path) # Your code here
                                self.last_valid_mod_time = mod_time


    from watchdog.observers import Observer
      
    event_handler = BackupHandler()
  
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
  
    observer.start()
    try:
        print(f"Listening... [DIR={path}]")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

async def async_watch(directory):
    import asyncio
    def fmt(flt):
        return f"{flt:.4f}"

    from watchfiles import awatch
    print(f"\nListening... [DIR={directory}]\n")

    ref_time = time.time()
    async for changes in awatch(directory):
        changes = list(changes)
        changes = [ (change.name, os.path.abspath(path)) for change, path in changes ]
        changes = [ (fmt(time.time()-ref_time), name, path) for name, path in changes if os.path.exists(path) ]
        filenames = list(set(path for _, _, path in changes))
        filenames = [ os.path.relpath(path, directory) for path in filenames ]
        rel_time = fmt(time.time()-ref_time)
        ref_time = time.time()
        await asyncio.sleep(5)


        # ic(changes)
        print(rel_time, filenames)

def print_thread_information():
    threads = [ thread for thread in threading.enumerate() ]
    ic(threads)

def wait_till_keyboard_interrupt():
    # is_main_thread = check_if_main_thread()
    # if is_main_thread:
    #     import signal
    #     signal.signal(signal.SIGINT, signal.SIG_DFL)
    global keyboard_event
    try:
        while not keyboard_event.is_set():
            keyboard_event.wait(0.1)
    except KeyboardInterrupt:
        keyboard_event.set()
        time.sleep(1)
        print_thread_information()

class Directories:

    def __init__(self):
        self.lock = threading.Lock()
        self.dir2status = {}

    def set_dirty(self, directory):
        lock = self.lock
        with lock:
            self.dir2status[directory] = 'DIRTY'

    def set_clean(self, directory):
        lock = self.lock
        with lock:
            self.dir2status[directory] = 'CLEAN'

def watch_fast(directories):

    def handle_event(path, rel_time, directory):
        abs_path = path
        mod_time = time.time()

        if os.path.exists(abs_path):
            not_vim_file = not abs_path.endswith("~")
            if not_vim_file:
                seconds_elapsed = rel_time
                get_tracked_filepaths_performant = Cache(get_tracked_filepaths, directory)
                tracked_filepaths = get_tracked_filepaths_performant()
                # tracked_filepaths = get_tracked_filepaths(directory)
                if abs_path in tracked_filepaths:
                    repo = git.Repo(directory)
                    is_dirty_performant = Cache(repo.is_dirty)
                    is_dirty = is_dirty_performant() # Takes 300ms
                    # is_dirty = repo.is_dirty() # Takes 300ms
                    if is_dirty:
                        dt = Date(mod_time).dt.strftime("%b %d %H:%M:%S")
                        elapsed_string = f"+{seconds_elapsed:.1f}s".rjust(len("+000.0s"))
                        elapsed_string = Code.RED + elapsed_string if seconds_elapsed < 1 else Code.GREEN + elapsed_string
                        gui_queue.put({ "directory": directory, "status": "DIRTY" })
                        print_safe(dt, elapsed_string, abs_path) # Your code here

    def expensive(changes, ref_time):
        nonlocal directories
        changes = list(changes)
        filenames = [ os.path.abspath(path) for _, path in changes ]
        filenames = list(set([ filename for filename in filenames if os.path.exists(filename) ]))
        rel_time = time.time()-ref_time
        for filename in filenames:
            directory = next(directory for directory in directories if filename.startswith(directory))
            handle_event(filename, rel_time, directory)
            rel_time = time.time()-ref_time

    def producer():
        from watchfiles import watch
        ref_time = time.time()
        for changes in watch(*directories, stop_event=keyboard_event):
            q.put((changes, ref_time))
            ref_time = time.time()

    def consumer():
        while not keyboard_event.is_set():
            if should_restart_watcher:
                break
            try:
                argument_tuple = q.get(timeout=1)
            except queue.Empty:
                continue
            expensive_thread = threading.Thread(target=expensive, args=argument_tuple, name="expensive-", daemon=True)
            expensive_thread.start()

    # commit_periodic {{{
    @logger.catch(reraise=True)
    def commit_periodic(directory):
        global commit_lock
        global poll_event
        global poll_rlock
        nonlocal directory_count
        nonlocal commit_date_D
        nonlocal cursor
        nonlocal connection
        from datetime import datetime
        wait_time = 15
        while not keyboard_event.is_set():
            if should_restart_watcher:
                break
            now = datetime.now()
            if now.second % wait_time == 0:
                date_string = now.strftime("%H:%M:%S")
                epoch = now.timestamp()
                repo = git.Repo(directory)
                if repo.is_dirty():
                    gui_queue.put({ "directory": directory, "status": "DIRTY" })
                    print_safe(f"\n[commit_periodic] DIRTY: {directory}")
                    time_taken, exception = backup(directory)
                    D = { "date_string": date_string, "epoch": epoch, "time_taken": time_taken, "status": "DIRTY", "exception": exception, "path": directory }
                    gui_queue.put({ "directory": directory, "status": "CLEAN" })
                else:
                    D = { "date_string": date_string, "epoch": epoch, "time_taken": None, "status": "CLEAN", "exception": None, "path": directory }
                    print_safe(f"[commit_periodic] CLEAN {directory}")
                    gui_queue.put({ "directory": directory, "status": "CLEAN" })
                with commit_lock:
                    cursor.execute("INSERT INTO backup VALUES (:date_string, :epoch, :time_taken, :status, :exception, :path);", D)
                    connection.commit()
                    key = date_string
                    commit_date_D[key] = commit_date_D.setdefault(key, 0) + 1
                    if commit_date_D[key] == directory_count:
                        # poll_event.set()
                        try:
                            start_time = time.time()
                            with poll_rlock:
                                session.get("http://127.0.0.1:5000/set_poll", timeout=1)
                            time_taken = time.time() - start_time
                            print_safe(f"GET /set_poll: {time_taken:.2f} seconds")
                        except requests.exceptions.ConnectionError as error_server_is_down:
                            pass
                        except requests.exceptions.Timeout as error_timeout:
                            pass
                keyboard_event.wait(1)
            else:
                seconds_remaining = wait_time - (now.second % wait_time)
                date_string = now.strftime("%b %d %H:%M:%S")
                print_safe(f"[{date_string}] REM={seconds_remaining:02d}", end="\r")
            keyboard_event.wait(0.1)
    # }}}

    # draw_icon {{{
    def draw_icon():
        # Fix DPI, blurry text and low-resolution icons and labels
        def create_image(width=64, height=64, color1='black', color2='white'):
            from PIL import Image, ImageDraw
            image = Image.new('RGB', (width, height), color1)
            dc = ImageDraw.Draw(image)
            dc.rectangle((width // 2,           0,      width, height // 2), fill=color2)
            dc.rectangle((         0, height // 2, width // 2, height), fill=color2)
            return image

        def change_color(icon, item):
            icon.icon = create_image(width=64, height=64, color1='red', color2='white')

        def icon_updater(icon):

            nonlocal main_item_1
            nonlocal is_stopped
            icon.visible = True
            clean_icon = create_image()
            dirty_icon = create_image(width=64, height=64, color1='red', color2='white')
            while not keyboard_event.is_set():
                if should_restart_watcher:
                    break
                if is_stopped:
                    break
                try:
                    D = gui_queue.get(timeout=1)
                    directory, status = D['directory'], D['status']
                    dir2status[directory] = status
                    all_clean = all(status == 'CLEAN' for status in dir2status.values())
                    icon.icon = clean_icon if all_clean else dirty_icon
                    clean_count = len([ status for status in dir2status.values() if status == 'CLEAN' ])
                    dirty_count = len([ status for status in dir2status.values() if status == 'DIRTY' ])
                    icon.title = f"Clean Directories: {clean_count}\nDirty Directories: {dirty_count}"

                except queue.Empty:
                    continue
            icon.stop()

        def get_clean_directories_as_items(x):
            from pystray import MenuItem as item
            return (item(directory, lambda x :x) for directory, status in dir2status.items() if status == 'CLEAN')

        def foo(x):
            print_safe(x)

        def stop_icon(icon):
            nonlocal is_stopped
            is_stopped = True
            icon.stop()


        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        is_stopped = False

        dir2status = { directory: 'CLEAN'  for directory in directories }
        from pystray import Icon as icon, Menu as menu, MenuItem as item
        stop_item = item('Exit', stop_icon)
        gui_item = item('GUI', gui)
        change_color_item = item('Change Icon', change_color)

        item_1 = item('Submenu item 1', lambda icon, item: print_safe("[draw_icon] 1"))
        item_2 = item('Submenu item 2', lambda icon, item: print_safe("[draw_icon] 2"))
        submenu = menu(item_1, item_2)
        main_item_1 = item('With submenu', submenu)

        clean_submenu = menu(
            lambda: item(f'clean-{i}', foo(i)) for i in range(5)
        )
        main_clean_item = item('Clean Paths', clean_submenu)


        main_menu = menu(main_item_1, change_color_item, gui_item, stop_item)
        m = icon('test', create_image(), title='backup.py', menu=main_menu).run(icon_updater)
        # main_icon = icon('test', create_image(), title='backup.py', menu=main_menu).run()
    # }}}

    global screen_lock
    global keyboard_event
    global should_restart_watcher
    import requests
    session = requests.Session()
    import queue
    q = queue.Queue()
    gui_queue = queue.Queue()
    directory_count = len(directories)
    commit_date_D = {}

    log_dir = get_log_db_path()
    cursor, connection = db_init(log_dir)
    cursor.execute("DROP TABLE backup;")
    cursor.execute("CREATE TABLE IF NOT EXISTS backup (date_string TEXT, epoch REAL, time_taken REAL, status TEXT, exception TEXT, path TEXT);")
    connection.commit()

    producer_thread = threading.Thread(target=producer, name="producer", daemon=False)
    consumer_thread = threading.Thread(target=consumer, name="consumer", daemon=False)
    draw_icon_thread = threading.Thread(target=draw_icon, name="draw_icon", daemon=False)

    commit_threads = [ threading.Thread(target=commit_periodic, args=(directory,), name=f"{os.path.basename(directory)}-commit") for directory in directories ]

    producer_thread.start()
    consumer_thread.start()
    draw_icon_thread.start()
    for commit_thread in commit_threads:
        commit_thread.start()

    # wait_till_keyboard_interrupt()
    try:
        while not keyboard_event.is_set():
            if should_restart_watcher:
                print_safe("Starting cleanup")
                # producer_thread.join()
                # print_safe("Finished producer_thread")
                consumer_thread.join()
                print_safe("Finished consumer_thread")
                for i, commit_thread in enumerate(commit_threads):
                    commit_thread.join()
                    print_safe(f"Finished commit_thread {i}")
                break # This terminates watch_fast, restarting onus is on launcher
            keyboard_event.wait(0.1)
    except KeyboardInterrupt:
        keyboard_event.set()
        time.sleep(1)
        print_thread_information()

class Cache:
    def __init__(self, func, *args):
        self.func = func
        self.args = args
        self.epoch = 0
        self.result = None
        self.timeout = 4.0

    def __call__(self):
        now = time.time()
        if self.result == None or now - self.epoch > self.timeout:
            self.result = self.func(*self.args)
            self.epoch = now
        return self.result

def pXY(x,y):
    time.sleep(1)
    return f"x = {x}, y={y}"


def launcher(no_server=False):

    def thread_info_printer():
        thread_name = threading.current_thread().name
        print_safe(Code.GREEN + "thread_info_printer: " + thread_name)
        global keyboard_event
        wait_time = 1
        iteration_count = 0
        flag = threading.Event()
        try:
            while not keyboard_event.is_set():
                iteration_count = iteration_count + 1
                thread_string = ", ".join([ thread.name for thread in threading.enumerate() ])
                # thread_string = "-- thread-string --"
                if threading.active_count() == 8:
                    flag.set()
                    wait_time = 100
                    print_safe(f"[safe] [IF] [{iteration_count}] Thread Count={threading.active_count()} Threads={thread_string} Wait Time: {wait_time} [Flag={keyboard_event.is_set()}]")
                    print_safe("")
                    # our_threads = [ thread for thread in threading.enumerate() ]
                    print_safe(Code.GREEN + "Hit assignment")
                    # print_safe(f"[safe] Thread Count={threading.active_count()} ", end="\r")

                else:
                    print_safe(f"[safe] [ELSE] [{iteration_count}]Thread Count={threading.active_count()} Threads={thread_string} Wait Time: {wait_time} [Flag={keyboard_event.is_set()}]", end="\r")
                    # print_safe("")
                # event.wait(wait_time)
                time.sleep(wait_time)
        except KeyboardInterrupt:
            keyboard_event.set()


    def zmq_server():
        global should_restart_watcher
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:5555")
        while not keyboard_event.is_set():
            try:
                D = socket.recv_json(flags=zmq.NOBLOCK)
            except zmq.ZMQError:
                time.sleep(0.1)
                continue
            print_safe(D)
            if D['restart_watcher']:
                print_safe("zmq_server() - Restart Watcher")
                should_restart_watcher = True
            response = { "status": 200 }
            socket.send_json(response)

    def get_paths():
        cursor, connection = db_init(get_data_db_path())
        paths = [ row['path'] for row in cursor.execute("SELECT * FROM paths").fetchall() ]
        paths = [ path for path in paths if is_git_repo(path) ]
        paths = [ path for path in paths if no_remote(git.Repo(path)) == False ]
        return paths
    
    global should_restart_watcher
    global keyboard_event

    paths = get_paths()
    if len(paths) == 0:
        print_safe(Code.RED + "No git repo’s with remotes found. Exit.")
        return

    # error_out_file = rel2abs("backup-flask/error.txt")
    # sys.stdout = open(error_out_file, 'w')
    # sys.stderr = sys.stdout
    # sys.stderr = open(error_out_file, 'w')

    ipc_thread = threading.Thread(target=zmq_server, name="zmq_server", daemon=False)
    watch_thread = threading.Thread(target=watch_fast, args=(paths,), name="watch_fast", daemon=False)
    # printer_thread = threading.Thread(target=thread_info_printer, name="info_printer", daemon=False)
    server_thread = threading.Thread(target=server, name="flask_thread", daemon=False)

    ipc_thread.start()
    watch_thread.start()
    # printer_thread.start()
    if not no_server:
        server_thread.start()

    try:
        while not keyboard_event.is_set():
            if should_restart_watcher:
                watch_thread.join()
                print_safe(Code.CYAN + "Restarting Watcher ... ", end="")
                paths = get_paths()
                if len(paths) == 0:
                    continue
                watch_thread = threading.Thread(target=watch_fast, args=(paths,), name="watch_fast", daemon=False)
                watch_thread.start()
                print_safe(Code.CYAN + "SUCCESS!")
                should_restart_watcher = False
            keyboard_event.wait(0.1)
    except KeyboardInterrupt:
        keyboard_event.set()
        time.sleep(1)
        print_thread_information()


def server_is_up():
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 5000))
    if result == 0:
       return True
    else:
       return False

def send_message_to_watcher():

    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    context = zmq.Context()
    print_safe("Connecting to hello world server…")
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    #  Do 10 requests, waiting each time for a response
    for index in range(10):
        print_safe("Sending request %s …" % index)
        socket.send(b"Hello")
        #  Get the reply.
        message = socket.recv()
        print_safe("Received reply %s [ %s ]" % (index, message))

def main():

    from colorama import init
    init(convert=True)
    if len(sys.argv) == 2 and sys.argv[1] == '--server':
        server()
        return
    if len(sys.argv) == 2 and sys.argv[1] == '--backup':
        launcher(no_server=True)
        return
    else:
        launcher()
        return

    return

    # backup(path)
    # server_1()
    # draw_icon()

    return

if __name__ == "__main__":
    with handler():
        main()
