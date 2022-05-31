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

import threading
screen_lock = threading.Lock()

is_overlap = False

def rel2abs(relative_path):
    frame            = sys._getframe(1)
    called_path      = frame.f_code.co_filename
    parent_directory = os.path.dirname(os.path.realpath(called_path))
    absolute_path    = os.path.realpath(os.path.join(parent_directory, relative_path))
    return absolute_path


# "."
def print_safe(s="", end="\n"):
    global is_overlap
    if end == "\r":
        is_overlap = True
    global screen_lock
    screen_lock.acquire()
    if is_overlap and end == "\n":
        is_overlap = False
        print()
    print(s, end=end)
    screen_lock.release()

def unused_silencer():
    Code, ic, ib

# commit-push [ tag auto-commits-on-change(5m window) ]
# daemon [ icon schedule watch ]
# import.py
# pipreqs.py

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
        print(Code.RED + "Install and add pipreqs to $PATH. `pip install pipreqs`")
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

    from glob import glob
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

def db_init(db_path):
    import platform
    if platform.system() == "Linux":
        import pysqlite3 as sqlite3
    else:
        import sqlite3
    data_dir = rel2abs("templates/data.db")
    print_safe(Code.GREEN + data_dir)
    connection = sqlite3.connect(data_dir, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    return cursor, connection

def server():
    # https://gist.github.com/gmolveau/10c80785d499c2e2d4c447343a624664
    from flask import Flask, render_template, jsonify, request
    import glob
    data_dir = rel2abs("templates/data.db")
    print_safe(Code.GREEN + data_dir)
    cursor, connection = db_init(data_dir)

    template_folder = rel2abs('templates')
    print_safe(Code.GREEN + template_folder)
    app = Flask(__name__, template_folder=template_folder)

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
        
        return render_template('gui.html', paths=paths, folder_payload=folder_payload)

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
        return "200"

    @app.route("/api/db_remove", methods=[ "DELETE" ])
    def db_remove():
        D = request.json
        path = D["path"]
        cursor.execute("DELETE FROM paths WHERE path=?;", (path,))
        connection.commit()
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

    def db():
        cursor.execute("CREATE TABLE IF NOT EXISTS paths (path TEXT UNIQUE);")
        connection.commit()

    db()
    is_main_thread = threading.current_thread() == threading.main_thread()
    app.run(host='0.0.0.0', use_reloader=is_main_thread, port=5000, debug=True)


def server_1():
    # import threading
    # threading.Thread(target=server, daemon=True).start()
    server()

def gui():
    
    filepath = 'http://localhost:5000'
    import subprocess, os, platform
    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
    else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))

def draw_icon():
    def create_image(width=64, height=64, color1='black', color2='white'):
        from PIL import Image, ImageDraw
        # Generate an image and draw a pattern
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.rectangle(
            (width // 2, 0, width, height // 2),
            fill=color2)
        dc.rectangle(
            (0, height // 2, width // 2, height),
            fill=color2)
        return image

    def change_color(icon, item):
        icon.icon = create_image(width=64, height=64, color1='red', color2='white')

    from pystray import Icon as icon, Menu as menu, MenuItem as item

    stop_item = item('Exit', lambda icon, item: icon.stop())
    gui_item = item('GUI', gui)
    change_color_item = item('Change Icon', change_color)
    item_1 = item('Submenu item 1', lambda icon, item: print("1"))
    item_2 = item('Submenu item 2', lambda icon, item: print("2"))
    submenu = menu(item_1, item_2)
    main_item_1 = item('With submenu', submenu)
    main_menu = menu(main_item_1, change_color_item, gui_item, stop_item)
    m = icon('test', create_image(), title='backup.py', menu=main_menu).run()

def get_tracked_filepaths(path):
    if not is_git_repo(path):
        print(Code.RED + f"No .git repostiory for {path}")
        print(Code.RED + "This was triggered in the watcher, so .git corruption could have occurred.")
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

def watch_fast(directory):
    global screen_lock
    import queue
    q = queue.Queue()
    event = threading.Event()

    def handle_event(path, rel_time):
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
                        screen_lock.acquire()
                        print(dt, elapsed_string, abs_path) # Your code here
                        screen_lock.release()

    def expensive(changes, ref_time):
        def fmt(flt):
            return f"{flt:.4f}"
        changes = list(changes)
        filenames = [ os.path.abspath(path) for _, path in changes ]
        filenames = list(set([ filename for filename in filenames if os.path.exists(filename) ]))
        relative_filenames = [ os.path.relpath(filename, directory) for filename in filenames ]
        rel_time = time.time()-ref_time
        for filename in filenames:
            handle_event(filename, rel_time)
            rel_time = time.time()-ref_time
        # print(rel_time, filenames)

    def producer(directory):
        from watchfiles import watch
        ref_time = time.time()
        for changes in watch(directory, stop_event=event):
            q.put((changes, ref_time))
            ref_time = time.time()

    def consumer():
        while not event.is_set():
            argument_tuple = q.get()
            expensive_thread = threading.Thread(target=expensive, args=argument_tuple, name="expensive-", daemon=True)
            expensive_thread.start()

    def commit_periodic():
        from datetime import datetime
        wait_time = 15
        while not event.is_set():
            if datetime.now().second % wait_time == 0:
                repo = git.Repo(directory)
                if repo.is_dirty():
                    print_safe()
                    print_safe(f"[commit_periodic] is-dirty: {directory}")
                    backup(directory)
                else:
                    print_safe(f"[commit_periodic] not-dirty {directory}")
                print_safe()
            else:
                seconds_remaining = wait_time - (datetime.now().second % wait_time)
                date_string = datetime.now().strftime("%b %d %H:%M:%S")
                print_safe(f"[{date_string}] REM={seconds_remaining:02d}", end="\r")
            event.wait(1)


    dirname = os.path.dirname(directory)
    producer_thread = threading.Thread(target=producer, name=f"{dirname}-producer", args=(directory,), daemon=False)
    consumer_thread = threading.Thread(target=consumer, name=f"{dirname}-consumer", daemon=False)
    commit_thread = threading.Thread(target=commit_periodic, name=f"{dirname}-commit")

    producer_thread.start()
    consumer_thread.start()
    commit_thread.start()

    try:
        while not event.is_set():
            # thread_string = ", ".join([ thread.name for thread in threading.enumerate() ])
            # print(f"Thread Count={threading.active_count()} Threads={thread_string}")
            event.wait(0.1)
    except KeyboardInterrupt:
        event.set()
        time.sleep(0.01)
        # thread_string = ", ".join([ thread.name for thread in threading.enumerate() ])
        # print(f"Thread Count={threading.active_count()} Threads={thread_string}")


def producer_consumer():
    import queue
    q = queue.Queue()
    event = threading.Event()

    def expensive(d):
        print(f"[expensive] d={d} START")
        event.wait(4)
        print(f"[expensive] d={d} STOP")

    def producer():
        for i in range(5):
            q.put(i)
        print("[producer] PUT=5")
        event.wait(3)
        for i in range(5, 10):
            q.put(i)
        print("[producer] PUT=10")

    def consumer():
        while not event.is_set():
            try:
                d = q.get_nowait()
                expensive_thread = threading.Thread(target=expensive, args=(d,), name=f"expensive-{d}")
                expensive_thread.start()
            except queue.Empty:
                event.wait(1)

    producer_thread = threading.Thread(target=producer, name="producer")
    consumer_thread = threading.Thread(target=consumer, name="consumer")

    producer_thread.start()
    consumer_thread.start()

    try:
        while not event.is_set():
            # thread_string = ", ".join([ thread.name for thread in threading.enumerate() ])
            # print(f"Thread Count={threading.active_count()} Threads={thread_string}")
            event.wait(1)
    except KeyboardInterrupt:
        event.set()


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

my_event = threading.Event()
def launcher():

    def thread_info_printer():
        thread_name = threading.current_thread().name
        print_safe(Code.GREEN + "thread_info_printer: " + thread_name)
        global my_event
        wait_time = 1
        iteration_count = 0
        flag = threading.Event()
        try:
            while not my_event.is_set():
                iteration_count = iteration_count + 1
                thread_string = ", ".join([ thread.name for thread in threading.enumerate() ])
                # thread_string = "-- thread-string --"
                if threading.active_count() == 8:
                    flag.set()
                    wait_time = 100
                    print_safe(f"[safe] [IF] [{iteration_count}] Thread Count={threading.active_count()} Threads={thread_string} Wait Time: {wait_time} [Flag={my_event.is_set()}]")
                    print_safe("")
                    # our_threads = [ thread for thread in threading.enumerate() ]
                    print_safe(Code.GREEN + "Hit assignment")
                    # print_safe(f"[safe] Thread Count={threading.active_count()} ", end="\r")

                else:
                    print_safe(f"[safe] [ELSE] [{iteration_count}]Thread Count={threading.active_count()} Threads={thread_string} Wait Time: {wait_time} [Flag={my_event.is_set()}]", end="\r")
                    # print_safe("")
                # event.wait(wait_time)
                time.sleep(wait_time)
        except KeyboardInterrupt:
            my_event.set()


    cursor, connection = db_init("templates/data.db")
    paths = [ row['path'] for row in cursor.execute("SELECT * FROM paths").fetchall() ]

    paths = [ path for path in paths if is_git_repo(path) ]
    paths = [ path for path in paths if no_remote(git.Repo(path)) == False ]
    if len(paths) == 0:
        print(Code.RED + "No git repo’s with remotes found. Exit.")
        return

    threads = []

    for path in paths:
        thread_name = os.path.basename(path)
        thread = threading.Thread(target=watch_fast, args=(path,), name=thread_name, daemon=False)
        threads.append(thread)

    printer_thread = threading.Thread(target=thread_info_printer, name="info_printer", daemon=False)
    server_thread = threading.Thread(target=server, name="flask_thread", daemon=False)

    for thread in threads:
        thread.start()

    # printer_thread.start()
    server_thread.start()
    # server()
    while True:
        my_event.wait(1)



def main():
    from colorama import init
    init(convert=True)
    launcher()
    return

    # value = "fortnite"
    # more = "apex"

    # # pX_performant = Cache(lambda :pX(value))
    # pXY_performant = Cache(pXY, value, more)
    # for i in range(5):
    #     fmt_string = pXY_performant()
    #     print(fmt_string)


    paths = [ r'C:\Users\vivek\Desktop\python_git' ]

    path = "~/Desktop/python_git"
    # path = "."
    if "~" in path:
        path = os.path.abspath(os.path.expanduser(path))
    elif "." in path:
        path = rel2abs(path)
        print_safe(Code.GREEN + path)
    else:
        path = os.path.abspath(path)
    # backup(path)
    server_1()
    draw_icon()
    #duGKzE

    # print("watch-fast")
    # watch_fast(path)
    return

    repo = git.Repo(path)
    # watch(path)
    import asyncio
    asyncio.run(async_watch(path))
    

if __name__ == "__main__":
    with handler():
        pass
        main()
