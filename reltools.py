
# IMPORTANT:
# 1. HAS TO BE IN THE SAME DIRECTORY AS COMMON IF YOU ARE IMPORTING THROUGH COMMON
# 2. get_caller_parent HAS TO BE IN SAME FILE AS rel2abs

# TODO:
# test stack deep-ness in 
#
#     reltools:write
#     reltools:read
#     db:db_init`

import os
import sys

def read(relpath):
    import json
    filepath = relpath if os.path.isabs(relpath) else rel2abs(relpath)
    filepath = os.path.normpath(filepath)
    with open(filepath, "r") as f:
        obj = json.load(f)
    return obj

def write(obj, relpath):
    import json
    filepath = os.path.normpath(rel2abs(relpath))
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(obj, f, indent=4)
    return filepath

def get_caller_parent():
    self_path = os.path.normpath(os.path.dirname(__file__))
    frame_index = 0
    directories = []
    while True:
        frame = sys._getframe(frame_index)
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

def rel2abs(relative_path):
    parent_directory = get_caller_parent()
    absolute_path    = os.path.realpath(os.path.join(parent_directory, relative_path))
    return absolute_path


