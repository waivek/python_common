"""


    INPUT  : arguments are file-storable: text, float, int, list(json), datetime(int)
    OUTPUT : returns are file-storable and can be compared for correctness when re-run with same inputs
    EPOCH  : time the function was called / run

Optional, Return value changes w.r.t. __file__ of caller
Exampe - rel2abs(string), ic()

    FILE   : File that called this function
    FUNC   : Function that called this function

"""

from timer import Timer   # Single Use
timer = Timer()
from color import Code    # Multi-Use
from error import handler # Single Use
from ic import ic, ib
ib; ic; Code

from datetime import datetime
import sys
import pickle
from time import time

gf = None
done = False
hash_to_trace_D = {}
path_function_pairs = []
trace_dictionaries = []
staging_D = {}

hashes = []
def frame_hash_to_trace_dictionaries_index(frame_hash):
    pass

def path_to_module_name(path):
    frame_index = 1
    while True:
        frame = sys._getframe(frame_index)
        if frame.f_code.co_filename == path:
            module_name = frame.f_globals['__name__']
            return module_name
        frame_index = frame_index + 1

def trace(function_names):
    if function_names == []:
        return
    global path_function_pairs
    frame = sys._getframe(1)
    filepath = frame.f_code.co_filename
    for function_name in function_names:
        pair = (filepath, function_name)
        path_function_pairs.append(pair)
    path_function_pairs = list(set(path_function_pairs))
    # import threading
    # threading.settrace(handle_trace_event)
    sys.settrace(handle_trace_event)

def rerun():
    global done
    done = True
    for trace_D in trace_dictionaries:
        result = pickle.loads(trace_D['result_pkl'])
        kwargs = pickle.loads(trace_D['kwargs_pkl'])
        function_name = trace_D['function_name']
        filepath = trace_D['filepath']
        function = get_function(filepath, function_name)
        calc_result = function(**kwargs)
        function_string = f"{function_name}(**{kwargs})"
        cmp_string = f"{function_string} == {repr(result)}"
        if calc_result == result:
            print(Code.GREEN + "✓", cmp_string)
        else:
             print(Code.RED + "✗", cmp_string)

import os.path
def handle_trace_event(frame, event, arg):
    print("handle_trace_event", event, os.path.basename(frame.f_code.co_filename), frame.f_code.co_name)
    global done
    global gf
    global hash_to_trace_D
    global path_function_pairs
    gf = frame
    if event.startswith("c_"):
        return

    # if frame.f_code.co_filename != __file__:
    #     return
    pair = (frame.f_code.co_filename, frame.f_code.co_name)
    if pair not in path_function_pairs:
        return
   
    if done:
        return

    frame_hash = hex(hash(frame))
    # ic(frame_hash)

    # function_D = hash_to_trace_D.get(frame_hash, {})
    function_D = staging_D.get(frame_hash, {})
    function_D["function_name"] = frame.f_code.co_name
    function_D["filepath"] = frame.f_code.co_filename
    if event == 'call':
        function_D["start_epoch"] = time()
        function_D["end_epoch"] = None
        function_D["kwargs_pkl"] = pickle.dumps(frame.f_locals)
        index = len(trace_dictionaries)
    elif event == 'return':
        function_D["end_epoch"] = time()
        function_D["result_pkl"] = pickle.dumps(arg)


    # hash_to_trace_D[frame_hash] = function_D
    if event == 'call':
        staging_D[frame_hash] = function_D
    elif event == 'return':
        trace_dictionaries.append(function_D)
        del staging_D[frame_hash]



def target(name: str, age: int, dob: datetime, face_bytes: bytes, items: list[str], maps: dict[str, str], known='Value'):
    global x
    # ic(locals())
    return "1, 2, 3"


def to_table(D):
    from ic import Table
    table = Table()
    for row in D.items():
        table.row(row)
    import textwrap
    table_string = "\n".join(str(table).split("\n")[1:])
    table_string = textwrap.dedent(table_string)
    return table_string

def greeting():
    print("Hello, World!")

def get_function(path, function_name):
    from importlib import import_module
    # import os.path
    # module_name,_ = os.path.splitext(os.path.basename(path))
    module_name = path_to_module_name(path)
    module = import_module(module_name, path)
    function = getattr(module, function_name)
    return function

def old_implementation():
    sys.setprofile(handle_trace_event)
    kwargs =  { "name" : "Vivek Bose", "age" : 27, "dob" : datetime(1994, 11, 7), "face_bytes" : bytes("FACE".encode("utf-8")), "items" : [ "Avocado", "Banana" ], "maps" : { "India": "Ruppee", "USA": "Dollar" } }
    # target(name="Vivek Bose", age=27, dob=datetime(1994, 11, 7), face_bytes=bytes("FACE".encode("utf-8")), items=[ "Avocado", "Banana" ], maps={ "India": "Ruppee", "USA": "Dollar" })
    target(**kwargs)

    global done
    done = True
    table = [ {
        'frame_hash': frame_hash,
        'function_name': trace_D['function_name'],
        'filepath': trace_D['filepath'],
        'start_epoch': trace_D['start_epoch'],
        'end_epoch': trace_D['end_epoch'],
        'result': pickle.loads(trace_D['result_pkl']),
        'kwargs': to_table(pickle.loads(trace_D['kwargs_pkl']))
    } for frame_hash, trace_D in hash_to_trace_D.items() ]

    # frame_hash = list(hash_to_trace_D.keys())[0]
    # ic(hash_to_trace_D[frame_hash])
    for frame_hash, trace_D in hash_to_trace_D.items():
        result = pickle.loads(trace_D['result_pkl'])
        kwargs = pickle.loads(trace_D['kwargs_pkl'])
        function_name = trace_D['function_name']
        filepath = trace_D['filepath']
        function = get_function(filepath, function_name)
        calc_result = function(**kwargs)
        function_string = f"{function_name}(**{kwargs})"
        if calc_result == result:
            print("TRUE", function_string)
        else:
             print("FALSE", function_string)

def add(x, y):
    # print(f"Sum Is: {x+y}")
    return x+y

def main():
    trace(['add'])
    result = add(1, 2)
    # import threading
    # thread = threading.Thread(target=add, args=[3, 4])
    # thread.start()
    # thread.join()
    print(trace_dictionaries)



if __name__ == "__main__":
    main(); exit()
    with handler():
        main()
