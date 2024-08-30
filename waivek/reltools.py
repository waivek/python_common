# IMPORTANT:
# 1. FILE HAS TO BE IN THE SAME DIRECTORY AS COMMON IF YOU ARE IMPORTING THROUGH COMMON
# 2. get_caller_parent HAS TO BE IN SAME FILE AS rel2abs

# TODO:
# test stack deep-ness in 
#
#     reltools:write
#     reltools:read
#     db:db_init`

import os
import sys
from waivek.color import Code

def pathjoin(frame, relpath):
    frame_directory = os.path.dirname(frame.f_code.co_filename)
    return os.path.realpath(os.path.join(frame_directory, relpath))

def readlines(relpath):
    """
    Read lines from a file.
    relpath can be relative or absolute. Resolved via rel2abs methodology.
    Leading and trailing whitespace is stripped.
    """
    path = relpath if os.path.isabs(relpath) else pathjoin(sys._getframe(1), relpath)
    if os.path.exists(path) is False:
        print(f"File not found: {Code.RED + path}")
    with open(path, "rb") as f:
        lines = f.read().decode("utf-8").strip().splitlines()
    return lines
    
def writelines(relpath, lines):

    """
    Write lines to a file.
    relpath can be relative or absolute. Resolved via rel2abs methodology.
    """
    path = relpath if os.path.isabs(relpath) else pathjoin(sys._getframe(1), relpath)
    with open(path, "wb") as f:
        f.write("\n".join(lines).encode("utf-8"))

def read(relpath):
    import json
    from waivek.color import Code
    filepath = relpath if os.path.isabs(relpath) else pathjoin(sys._getframe(1), relpath)
    filepath = os.path.normpath(filepath)
    if os.path.exists(filepath) is False:
        message = "[reltools.py:read()] " + (Code.YELLOW + "File does not exist: ") + (Code.RED + filepath)
        print(message)
        return {}

    with open(filepath, "r") as f:
        obj = json.load(f)
    return obj

def write(obj : list | dict, relpath: str) -> str:
    import json
    filepath = relpath if os.path.isabs(relpath) else pathjoin(sys._getframe(1), relpath)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(obj, f, indent=4)
    return filepath

def get_caller_parent():
    from waivek.frame import Frame
    self_path = os.path.normpath(os.path.dirname(__file__))
    frame_index = 0
    directories = []
    frames = []
    while True:
        frame = sys._getframe(frame_index)
        frames.append(Frame(frame))
        called_path      = frame.f_code.co_filename
        parent_directory = os.path.dirname(os.path.realpath(called_path))
        directories.append(parent_directory)
        if parent_directory.lower() != self_path.lower():
            break
        if frame.f_back == None:
            break
        frame_index = frame_index + 1


    if frame.f_back is None and len(set(directories)) == 1 and directories[0] == os.path.dirname(__file__): # importing from a python file in same directory as reltools.py
        return directories[0]

    return parent_directory

def frame_to_absolute_directory(frame):
    return os.path.dirname(os.path.realpath(frame.f_code.co_filename))

def rel2abs(relative_path):
    from waivek.ic import ic
    from waivek.ic import ib
    return pathjoin(sys._getframe(1), relative_path)

    # Implementation 3
    # ================
    parent_directory = os.path.dirname(sys._getframe(1).f_globals["__file__"])
    absolute_path = os.path.realpath(os.path.join(parent_directory, relative_path))
    ic(absolute_path)
    return absolute_path

    # self_function_name = sys._getframe(0).f_code.co_name

    # Implementation 2
    # ================
    frame = sys._getframe(1)
    parent_directory = frame_to_absolute_directory(frame)
    absolute_path    = os.path.realpath(os.path.join(parent_directory, relative_path))
    ic(absolute_path)


    # Implementation 1
    # ================
    # parent_directory = get_caller_parent()
    # absolute_path    = os.path.realpath(os.path.join(parent_directory, relative_path))
    # ic(absolute_path)

    return absolute_path

def here():
    # importing pathlib is slow as shit
    # return Path(sys._getframe(1).f_code.co_filename).parent
    return os.path.dirname(os.path.realpath(sys._getframe(1).f_code.co_filename))

