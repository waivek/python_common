import sys; sys.path = [ "C:/users/vivek/Documents/Python/" ] + sys.path
from timer import Timer   # Single Use
timer = Timer()
from color import Code    # Multi-Use
from error import handler # Single Use
from ic import ic, ib     # Multi-Use, import time: 70ms - 110ms
Code; ic; ib; handler
from reltools import rel2abs

def main():
    # ic(get_tracked_python_files())
    # ic(get_untracked_python_files())
    # ic(get_python_files())
    ic(get_non_python_files())

def get_directories():
    from glob import glob
    import os.path
    current_dir = rel2abs(".")
    paths = glob(os.path.join(current_dir, "**/"), recursive=True)
    relpaths = [ os.path.relpath(path, current_dir) for path in paths ]
    return relpaths

def get_non_python_files():
    from glob import glob
    import os.path
    current_dir = rel2abs(".")
    paths = glob(os.path.join(current_dir, "*"), recursive=False)
    paths = [ path for path in paths if os.path.isfile(path) ]
    relpaths = [ os.path.relpath(path, current_dir) for path in paths ]
    relpaths = [ path for path in relpaths if not path.endswith(".py") ]
    return relpaths

def get_python_files():
    from glob import glob
    import os.path
    current_dir = rel2abs(".")
    paths = glob(os.path.join(current_dir, "**/*.py"), recursive=True)
    relpaths = [ os.path.relpath(path, current_dir) for path in paths ]
    return relpaths

def get_tracked_python_files():
    import git
    repo = git.Repo(".")
    tracked_files = repo.git.ls_files().split("\n")
    tracked_files = [ file for file in tracked_files if file.endswith(".py") ]
    return tracked_files

def get_untracked_python_files():
    import git
    repo = git.Repo(".")
    untracked_files = repo.untracked_files
    untracked_files = [ file for file in untracked_files if file.endswith(".py") ]
    return untracked_files

if __name__ == "__main__":
    with handler():
        main()

