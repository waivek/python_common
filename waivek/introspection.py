from waivek.timer import Timer   # Single Use
timer = Timer(precision=3)
from waivek.error import handler # Single Use
from waivek.color import Code    # Multi-Use
from waivek.ic import ic
from waivek.frame import Frame # takes 0.005s cuz of `ast` and `linecache`

class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age

def get_function_call_node(line, fname):
    import ast
    tree = ast.parse(line)
    call_node = ast.Call()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id == fname:
                    call_node = node
                    break
    return call_node

def noop(*__x__):
    pass


def pack(*args):
    noop(args)
    current_function_name = Frame(0).function_name

    frame = Frame(1)
    line = frame.line.strip()
    node = get_function_call_node(line, current_function_name)

    return { arg.id: frame.locals[arg.id] for arg in node.args }

def unpack_error_handling(variables, obj, rename_D, line):
    is_dict = isinstance(obj, dict)
    D = obj if is_dict else obj.__dict__

    
    rename_D = rename_D or {}
    combined_D = { **D, **rename_D }
    unknown_variables = [ var for var in variables if var not in combined_D ]
    if len(unknown_variables) == 0:
        return True


    print((Code.LIGHTBLACK_EX + "Error : ") + (Code.RED + "Unknown Variables"))
    # import os.path
    # frame = Frame(0)
    # path = os.path.relpath(frame.path, os.getcwd())
    # print((Code.LIGHTBLACK_EX + "Filename : ") + (Code.RED + f"{path}"))
    # print((Code.LIGHTBLACK_EX + "Function : ") + (Code.RED + f"{frame.function_name}"))
    for var in unknown_variables:
        line = line.replace(var, Code.RED + var)
    print((Code.LIGHTBLACK_EX + "Line  : ") + line)
    print()
    return False

# nested destructuring
# *L type destructuring?
# def unpack(obj, rename_D=None):

def unpack(obj, rename_D={}) -> tuple:
    from operator import itemgetter
    is_dict = isinstance(obj, dict)
    D = obj if is_dict else obj.__dict__

    frame = Frame(1)
    lhs = frame.line.split("=")[0].strip().replace("[", "").replace("]", "")
    variables = [var.strip() for var in lhs.split(",")]


    if not unpack_error_handling(variables, D, rename_D, frame.line.strip()):
        return (None,) * len(variables)

    # variables = [ var if var in D else rename_D[var] for var in variables ]
    variables = [ rename_D.get(var, var) for var in variables ]
    return itemgetter(*variables)(D)

def main():
    letter_1 = 'a'
    letter_2 = 'b'
    [ letter_1, letter_2 ] = unpack(pack(letter_1, letter_2))
    ic(letter_1, letter_2)
    print()
    
    D = { "a": 1, "b": 2, "c": 3 }
    [ a, clip_id ] = unpack(D, {"clip_id": "c"})
    ic(a, clip_id)
    print()
    user = User("John", 20)
    [ name, age ] = unpack(user)
    ic(name, age)
    print()

if __name__ == "__main__":
    with handler():
        main()

# run.vim: vert term python waivek/__init__.py
