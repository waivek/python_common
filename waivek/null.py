from waivek import Timer   # Single Use
timer = Timer()
from waivek import Code    # Multi-Use
from waivek import handler # Single Use
from waivek import ic, ib     # Multi-Use, import time: 70ms - 110ms
from waivek import rel2abs
Code; ic; ib; rel2abs

import sys
import json
import ast
import inspect

def query_1():
    return """{
        "a": 1,
        "b": {
            "c": 2,
            "d": 3
        }
    }"""

def query_2():
    return "{}"

def main():
    # code_line = 'm2 = D2[get()][name]["c"]'
    # variable_name = find_variable_accessed_by_key(code_line, 'b')
    # ic(variable_name)
    # return
    D1 = json.loads(query_1())
    resp2 = query_2()
    D2 = json.loads(resp2)
    name = "b"
    m1 = D1[name]["c"]
    m2 = D2[name]["c"]
    current_frame = sys._getframe()
    current_function = current_frame.f_code.co_name
    # function to source text, import if reqd
    source = inspect.getsource(current_frame.f_code)
    print(source)

def find_variable_accessed_by_key(code_line, target_key):
    import astor
    tree = ast.parse(code_line)
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript):
            subscript_node = node.slice
            ic(astor.to_source(subscript_node))
    return None

def investigate(e):
    from waivek.introspection import Frame
    import traceback
    tb = e.__traceback__
    frames = [ frame for frame, _ in traceback.walk_tb(tb) ]
    frame = frames[1]

    function_line_start = frame.f_code.co_firstlineno
    function_line_error = frame.f_lineno
    source = inspect.getsource(frame.f_code)
    # print source, but highlight the error line
    lines = source.split("\n")
    print(e)
    for i, line in enumerate(lines):
        if i == function_line_error - function_line_start:
            print(">>>", line)
            # we know it’s asn assignment error. we know the key. find the assignment dict that the key is referencing from the line
            # use ast.parse or anythign else if reqd
            



        else:
            print("   ", line)


if __name__ == "__main__":
    # with handler():
    #     main()
    try:
        main()
    except Exception as e:
        investigate(e)

