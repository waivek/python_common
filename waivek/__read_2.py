
import os
import stat
import json
import sys

def pathjoin(frame, relpath):
    frame_directory = os.path.dirname(frame.f_code.co_filename)
    return os.path.realpath(os.path.join(frame_directory, relpath))

def raise_for_file_not_found(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File does not exist: {path}")

def raise_for_file_empty(path):
    if os.stat(path).st_size == 0:
        raise ValueError(f"File is empty: {path}")

# we have a path we want to write to. it’s fine if the file doesn’t exist, but the directory must exist.
def raise_for_directory_not_found(path):
    if not os.path.exists(os.path.dirname(path)):
        raise FileNotFoundError(f"Directory does not exist: {os.path.dirname(path)}")

def readjson(relpath):
    path = relpath if os.path.isabs(relpath) else pathjoin(sys._getframe(1), relpath)
    raise_for_file_not_found(path)
    raise_for_file_empty(path)
    try:
        with open(path, "r") as f:
            obj = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"File is not parsable as json: {path}")
    return obj

def read_utf8(relpath):
    path = relpath if os.path.isabs(relpath) else pathjoin(sys._getframe(1), relpath)
    raise_for_file_not_found(path)
    raise_for_file_empty(path)
    with open(path, "rb") as f:
        string = f.read().decode("utf-8")
    return string

def readlines(relpath):
    path = relpath if os.path.isabs(relpath) else pathjoin(sys._getframe(1), relpath)
    raise_for_file_not_found(path)
    raise_for_file_empty(path)
    string = read_utf8(path)
    lines = string.strip().splitlines()
    return lines

def readstring(relpath):
    path = relpath if os.path.isabs(relpath) else pathjoin(sys._getframe(1), relpath)
    raise_for_file_not_found(path)
    raise_for_file_empty(path)
    with open(path, "rb") as f:
        string = f.read().decode("utf-8")
    return string

def writejson(obj, relpath):
    path = relpath if os.path.isabs(relpath) else pathjoin(sys._getframe(1), relpath)
    raise_for_directory_not_found(path)
    with open(path, "w") as f:
        json.dump(obj, f, indent=4)
    return path

def writelines(lines, relpath):
    path = relpath if os.path.isabs(relpath) else pathjoin(sys._getframe(1), relpath)
    raise_for_directory_not_found(path)
    with open(path, "wb") as f:
        f.write("\n".join(lines).encode("utf-8"))
    return path

def writestring(string, relpath):
    path = relpath if os.path.isabs(relpath) else pathjoin(sys._getframe(1), relpath)
    raise_for_directory_not_found(path)
    with open(path, "wb") as f:
        f.write(string.encode("utf-8"))
    return path

