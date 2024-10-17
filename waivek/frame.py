from waivek.timer import Timer   # Single Use
timer = Timer(precision=3)
import sys
import ast # takes 0.002s
import linecache # takes 0.003s
from waivek.color import Code    # Multi-Use
from waivek.error import handler # Single Use
from waivek.ic import ic, ib     # Multi-Use, import time: 70ms - 110ms

from types import FrameType

path2lines: dict[str, list[str]] = {}

class Frame:
    def __init__(self, frame_or_int):
        if isinstance(frame_or_int, int):
            frame = sys._getframe(frame_or_int+1)
        elif isinstance(frame_or_int, FrameType):
            frame = frame_or_int
        self.path = frame.f_code.co_filename
        self.lineno = frame.f_lineno
        self.line = getline(self.path, self.lineno)
        self.locals = frame.f_locals
        self.function_name = frame.f_code.co_name
        function_args = frame.f_code.co_varnames[:frame.f_code.co_argcount]
        function_arg_values = [ frame.f_locals[name] for name in function_args ]
        self.args = { name: value for name, value in zip(function_args, function_arg_values) }
        self.raw = frame
        # frame.f_back, frame.f_globals
    def print(self):
        import os.path
        argument_string = ", ".join([ f"{name}" for name, value in self.args.items() ])
        comment_string = ", ".join([ f"{name}={value}" for name, value in self.args.items() ])
        relpath = os.path.relpath(self.path, os.getcwd())
        location = Code.LIGHTBLACK_EX + f"{relpath}:{self.lineno}"
        function = f"{self.function_name}({argument_string})" 
        comment = Code.LIGHTBLACK_EX + f"# {comment_string}"
        print(" ".join([location, function, comment]))

def getline(path: str, lineno: int):
    global path2lines
    if path not in path2lines:
        with open(path, "rb") as f:
            lines = f.read().decode("utf-8").split("\n")
            path2lines[path] = lines
    index = lineno-1
    lines = path2lines[path]
    return lines[index]

def inspect_dot_stack():
    frames = [ sys._getframe(1) ]
    while frame := frames[-1].f_back:
        frames.append(frame)
    return [ Frame(frame) for frame in frames ]

def frame_gen():
    frame = sys._getframe(1)
    while frame:
        yield frame
        frame = frame.f_back


# IMPLEMENTATION 1: Doesnt Work
# =================
def to_dict(*variables):
    current_function_name = sys._getframe(0).f_code.co_name
    frame = sys._getframe(1)
    line = linecache.getline(frame.f_code.co_filename, frame.f_lineno).strip()
    # inside_string = line.split(current_function_name)[1][1:-1]
    inside_string = line.replace(current_function_name, "")[1:-1]
    names = [ name.strip() for name in inside_string.split(",") ]
    D = { name: frame.f_locals[name] for name in names }
    return D

# IMPLEMENTATION 2:
# =================
def create_dict(*args):
    frame = sys._getframe(1)
    node = ast.parse(linecache.getline(frame.f_code.co_filename, frame.f_lineno).strip()).body[0].value
    return { arg.id: frame.f_locals[arg.id] for arg in node.args }



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

    ic(getline(__file__, 6))
    return

    from datetime import datetime
    import re
    result = re.split('a', 'bab')
    datetime.now()
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
