
# SETTRACE vs. SETPROFILE
# =======================
#
# https://stackoverflow.com/a/59088868
#
# sys.settrace() only reports on Python code, not built-in callables or those defined in compiled extensions
#
# When using sys.settrace() returning a function object instead of None lets you trace other events within the frame,
# this is the 'local' trace function. You can re-use the same function object for this. You can disable per-line events
# by setting `frame.f_trace_lines = False`.


"""


    INPUT  : arguments are file-storable: text, float, int, list(json), datetime(int)
    OUTPUT : returns are file-storable and can be compared for correctness when re-run with same inputs
    EPOCH  : time the function was called / run

Optional, Return value changes w.r.t. __file__ of caller
Exampe - rel2abs(string), ic()

    FILE   : File that called this function
    FUNC   : Function that called this function

"""

from waivek.timer import Timer   # Single Use
timer = Timer()
from waivek.color import Code    # Multi-Use
from waivek.error import handler # Single Use
from waivek.ic import ic, ib
ib; ic; Code

from datetime import datetime
import sys
import pickle
from time import time
import os.path

gf = None
path_function_pairs = []
trace_dictionaries = []
total_time = 0

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
    import threading
    threading.settrace(handle_trace_event)
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




def target(name: str, age: int, dob: datetime, face_bytes: bytes, items: list[str], maps: dict[str, str], known='Value'):
    global x
    # ic(locals())
    return "1, 2, 3"


def to_table(D):
    from waivek.ic import Table
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

def add(x, y):
    # print(f"Sum Is: {x+y}")
    return x+y


def call_and_return_tracer(frame, event, arg, events = []):
    global total_time
    start = time()
    print("handle_trace_event", event, os.path.basename(frame.f_code.co_filename), frame.f_code.co_name)
    if event == 'call':
        print(f"Entering: {frame.f_code.co_name}")
        frame.f_trace_lines = False
        events.append(event)
        print(f"Entering: (event): {events!r}")
        total_time = total_time + time() - start
        return call_and_return_tracer
    elif event == 'return':
        events.append(event)
        print(f"Returning: {arg!r}")
        print(f"Returning (event): {events!r}")
        total_time = total_time + time() - start

def handle_trace_event(frame, event, arg, function_D = {}):
    # print("handle_trace_event", event, os.path.basename(frame.f_code.co_filename), frame.f_code.co_name)
    global total_time
    global gf
    global path_function_pairs
    start = time()
    gf = frame
    if event.startswith("c_"):
        return

    pair = (frame.f_code.co_filename, frame.f_code.co_name)
    if pair not in path_function_pairs:
        return
   
    # done = False
    # if done:
    #     return

    frame_hash = hex(hash(frame))

    function_D["function_name"] = frame.f_code.co_name
    function_D["filepath"] = frame.f_code.co_filename
    if event == 'call':
        function_D["start_epoch"] = time()
        function_D["end_epoch"] = None
        function_D["kwargs_pkl"] = pickle.dumps(frame.f_locals)
        frame.f_trace_lines = False
        total_time = total_time + time() - start
        return handle_trace_event
    elif event == 'return':
        function_D["end_epoch"] = time()
        function_D["result_pkl"] = pickle.dumps(arg)

    if event == 'return':
        trace_dictionaries.append(function_D)
        total_time = total_time + time() - start

def main():
    trace(['add'])
    # sys.settrace(call_and_return_tracer)
    # foo(spam, "universe")
    # for i in range(10):
    #     add(1, 2)
    import threading
    thread = threading.Thread(target=add, args=[3, 4])
    thread.start()
    thread.join()
    ic(trace_dictionaries)



if __name__ == "__main__":
    main(); exit()
    with handler():
        main()
