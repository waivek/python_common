import sys; sys.path = [ "C:/users/vivek/Documents/Python/" ] + sys.path
from timer import Timer   # Single Use
timer = Timer()
timer.start("frame.py")
import ast
import linecache
from color import Code    # Multi-Use
from error import handler # Single Use
from ic import ic, ib     # Multi-Use, import time: 70ms - 110ms


def repr_exists(obj):
    string = repr(obj)
    if string[0] != '<' or string[-1] != '>':
        return True
    import re
    m = re.match(r'\<.* object at 0x[0-9A-F]+\>', string)
    if m is None:
        return True
    else:
        return False
    # '<color.Maker object at 0x00000220322BB5E0>'

def unused_silencer():
    Code, ic, ib

def call_node_to_string(node, local_D):
    for index, arg in enumerate(node.args):
        match type(arg):
            case ast.Name:
                value = local_D[arg.id]
                if repr_exists(value):
                    node.args[index] = ast.Constant(local_D[arg.id])
                else:
                    A = repr(value.__class__.__name__)
                    C = repr(value.__dict__)
                    value_repr = f"type({A}, ({value.__class__.__name__},), {C})"
                    value_call = ast.parse(value_repr).body[0].value
                    node.args[index] = value_call

            case ast.Call:
                node.args[index] = call_node_to_string(arg, local_D)

    # print(ast.unparse(node))
    return node

def create_dict(*args):
    frame = sys._getframe(1)
    node = ast.parse(linecache.getline(frame.f_code.co_filename, frame.f_lineno).strip()).body[0].value
    return { arg.id: frame.f_locals[arg.id] for arg in node.args }

def frame_pretty():

    caller = sys._getframe(2)

    caller_path = caller.f_code.co_filename
    caller_lineno = caller.f_lineno
    caller_line = linecache.getline(caller_path, caller_lineno).strip()
    caller_node = ast.parse(caller_line).body[0].value
    caller_locals = caller.f_locals

    # ic(D)
    caller_line
    eval_line = ast.unparse(call_node_to_string(caller_node, caller_locals))
    D = {
        "lineno": caller_lineno,
        "path"  : caller_path,
        "line": caller_line,
        "eval_line": eval_line
    }
    ic(D)




def bar(z):
    return 'Blast'

class Point:
    def __init__(self, item):
        from random import randint
        self.item = item
        self.value = randint(0, 100)
    def ten():
        return 10

# foo    (x, y, 1, 'Sup', bar(z), [1, 2, 3, 4, 5], now, pt)
def foo(x, y, u,     z, result,               L,  dt, pt, string='Hello'):
    frames = sys._current_frames()
    frame_pretty()
    print(pt.value)
    return x + y

def main():

    from datetime import datetime
    x = 1
    y = 2
    z = 3
    pt = Point(1)
    now = datetime.now()
    # ic(repr_exists(1))
    # ic(repr_exists(now))
    # ic(repr_exists(pt))
    L = [1, 2, 3, 4, 5]
    foo(x, y, 1, 'Sup', bar(z), [1, 2, 3, 4, 5], now, pt)
    # create_dict(x, y)

if __name__ == "__main__":

    with handler():
        main()
timer.print("frame.py")
