# IMPORTANT:
# 1. HAS TO BE IN THE SAME DIRECTORY AS COMMON IF YOU ARE IMPORTING THROUGH COMMON
# 2. get_caller_parent HAS TO BE IN SAME FILE AS rel2abs

# TODO:
# test stack deep-ness in 
#
#     reltools:write
#     reltools:read
#     db:db_init`

import json
import os
import sys

def read(relpath):
    filepath = relpath if os.path.isabs(relpath) else rel2abs(relpath)
    filepath = os.path.normpath(filepath)
    with open(filepath, "r") as f:
        obj = json.load(f)
    return obj

def write(obj, relpath):
    filepath = os.path.normpath(rel2abs(relpath))
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(obj, f, indent=4)
    return filepath

def get_caller_parent():
    self_path = os.path.normpath(os.path.dirname(__file__))
    frame_index = 0
    while True:
        frame = sys._getframe(frame_index)
        called_path      = frame.f_code.co_filename
        parent_directory = os.path.dirname(os.path.realpath(called_path))
        if parent_directory.lower() != self_path.lower():
            break
        frame_index = frame_index + 1
        # co_name = frame.f_code.co_name
    return parent_directory

def rel2abs(relative_path):
    parent_directory = get_caller_parent()
    absolute_path    = os.path.realpath(os.path.join(parent_directory, relative_path))
    return absolute_path

