from waivek.timer import Timer
timer = Timer(precision=3)

from typing import TYPE_CHECKING # takes 0.01s
if TYPE_CHECKING:
    import pdb

import sys
from typing import Optional, List
from contextlib import contextmanager
from types import FrameType, TracebackType

from waivek.json_decode_error import handle_json_decode_error

# color_arg, color_error_repr, print_error_information {{{
def color_arg(arg):
    BLACK           = '\x1b[30m'
    RED             = '\x1b[31m'
    GREEN           = '\x1b[32m'
    YELLOW          = '\x1b[33m'
    BLUE            = '\x1b[34m'
    MAGENTA         = '\x1b[35m'
    CYAN            = '\x1b[36m'
    WHITE           = '\x1b[37m'
    LIGHTBLACK_EX   = '\x1b[90m'
    LIGHTRED_EX     = '\x1b[91m'
    LIGHTGREEN_EX   = '\x1b[92m'
    LIGHTYELLOW_EX  = '\x1b[93m'
    LIGHTBLUE_EX    = '\x1b[94m'
    LIGHTMAGENTA_EX = '\x1b[95m'
    LIGHTCYAN_EX    = '\x1b[96m'
    LIGHTWHITE_EX   = '\x1b[97m'
    RESET = '\x1b[39m'

    if type(arg) == str:
        arg = YELLOW + repr(arg)
    else:
        arg = CYAN + repr(arg)
    return arg

def color_error_repr(error):
    BLACK           = '\x1b[30m'
    RED             = '\x1b[31m'
    GREEN           = '\x1b[32m'
    YELLOW          = '\x1b[33m'
    BLUE            = '\x1b[34m'
    MAGENTA         = '\x1b[35m'
    CYAN            = '\x1b[36m'
    WHITE           = '\x1b[37m'
    LIGHTBLACK_EX   = '\x1b[90m'
    LIGHTRED_EX     = '\x1b[91m'
    LIGHTGREEN_EX   = '\x1b[92m'
    LIGHTYELLOW_EX  = '\x1b[93m'
    LIGHTBLUE_EX    = '\x1b[94m'
    LIGHTMAGENTA_EX = '\x1b[95m'
    LIGHTCYAN_EX    = '\x1b[96m'
    LIGHTWHITE_EX   = '\x1b[97m'
    BOLD            = '\x1b[1m'
    RESET           = '\x1b[39m'
    RESET_ALL       = '\x1b[0m'
    NORMAL          = '\x1b[22m'

    string = repr(error)
    args = ', '.join(color_arg(arg) for arg in error.args)
    colored_string = BOLD + f"{BOLD + LIGHTRED_EX}{error.__class__.__name__}{NORMAL}({YELLOW}{args}{LIGHTRED_EX}){RESET}" 
    return colored_string
    # lhs = Code.LIGHTRED_EX + m.group(1) 
    # middle =  Code.YELLOW + m.group(2) 
    # # middle = re.sub(r"('\w+')", Code.LIGHTCYAN_EX + r'\1', middle)
    # rhs = Code.LIGHTRED_EX + m.group(3)
    # colored_string = lhs + middle + rhs
    return colored_string

def print_error_information(error: Exception, frame_to_green: FrameType):
    # C:\Users\vivek\Documents\Python                               -> ~/Documents/Python
    # C:\Users\vivek\AppData\Roaming\Python\Python310\site-packages -> $APPDATA/Python/site-packages
    # C:\Program Files\Python310\Lib\site-packages                  -> 
    import traceback
    import os
    from pathlib import Path

    tb = error.__traceback__

    print()
    print(color_error_repr(error))
    # print(Code.LIGHTRED_EX + repr(error))

    from waivek.frame import frame_gen
    from waivek.color import Code
    call_frames = list(frame_gen())
    call_file = call_frames[3].f_code.co_filename

    frames = [ frame for frame, _ in traceback.walk_tb(tb) ]

    summaries = traceback.extract_tb(tb)
    pairs = reversed(list(zip(frames, summaries)))
    
    from waivek.ic import Table
    table = Table()
    table.gutter = '    '
    table.separator = ' ... '

    for i, (frame, summary) in enumerate(pairs):
        filepath = summary.filename
        filepath = str(Path(filepath).resolve()) # C:\users -> C:\Users
        if os.getcwd() in filepath:
            filepath = os.path.relpath(os.path.abspath(filepath))
        else:
            homedir = os.path.expanduser("~")
            filepath = filepath.replace(homedir, "~")

        line_number = summary.lineno
        line = summary.line
        # line = Code.LIGHTGREEN_EX + line if i == 0 else line
        # if green_done is False and frame.f_code.co_filename == call_file:
        if frame == frame_to_green:
            line = Code.LIGHTGREEN_EX + line
            line = '\x1b[1m' + line + '\x1b[22m'

            green_done = True
        lhs_string = f"{filepath}:{line_number}"
        table.row([lhs_string, line])
    table_string = str(table)
    table_lines = table_string.split("\n")
    table_lines = table_lines[1:]
    table_string = "\n".join(table_lines)
    print(table_string)
# }}}

def framestr(frame: FrameType) -> str:
    with open(frame.f_code.co_filename) as f:
        lines = f.readlines()
    line = lines[frame.f_lineno - 1].strip()
    return f'<frame> {frame.f_code.co_filename}:{frame.f_lineno} {line}'

def _select_frame_silent(self: "pdb.Pdb", number: int):
    assert 0 <= number < len(self.stack)
    self.curindex = number
    self.curframe = self.stack[self.curindex][0]
    self.curframe_locals = self.curframe.f_locals
    self.lineno = None

def do_down_silent(self: "pdb.Pdb", arg: int):
    if self.curindex + 1 == len(self.stack):
        print('Newest frame')
        return
    count = arg
    if count < 0:
        newframe = len(self.stack) - 1
    else:
        newframe = min(len(self.stack) - 1, self.curindex + count)
    _select_frame_silent(self, newframe)

def do_up_silent(self: "pdb.Pdb", error: Exception, arg: int):
    if self.curindex == 0:
        print('Oldest frame')
        return
    count = arg
    if count < 0:
        newframe = 0
    else:
        newframe = max(0, self.curindex - count)
    _select_frame_silent(self, newframe)

def x_three(self: "pdb.Pdb", error: Exception, arg):
    """
    Move up the stack by `arg` frames and print the stack frame
    """
    do_up_silent(self, error, arg)
    assert self.curframe
    print_error_information(error, self.curframe)

def make_x_one(self: "pdb.Pdb", error: Exception):
    def x_one(arg):
        if arg == '':
            arg = 1
        else:
            arg = int(arg)
        x_three(self, error, arg)
    return x_one

def y_three(self: "pdb.Pdb", error: Exception, arg):
    """
    Move down the stack by `arg` frames and print the stack frame
    """
    do_down_silent(self, arg)
    assert self.curframe
    print_error_information(error, self.curframe)

def make_y_one(self: "pdb.Pdb", error: Exception):
    def y_one(arg):
        if arg == '':
            arg = 1
        else:
            arg = int(arg)
        y_three(self, error, arg)
    return y_one

def make_v_zero_arg(self: "pdb.Pdb", error: Exception):
    """
    Print the variables in the current stack frame
    """
    from waivek.error import print_variables
    def v_zero_arg(*args):
        assert self.curframe
        print_variables(self.curframe.f_locals)
    return v_zero_arg

def make_z_zero_arg(self: "pdb.Pdb", error: Exception):
    """
    Print the stack frame
    """
    def z_zero_arg(*args):
        assert self.curframe
        print_error_information(error, self.curframe)
    return z_zero_arg

def ic_two(self: "pdb.Pdb", arg):
    from waivek.ic import ic
    assert self.curframe
    val = eval(arg, self.curframe.f_globals, self.curframe.f_locals)
    ic(val)

def make_ic_one_arg(self: "pdb.Pdb"):
    def ic_one(arg):
        ic_two(self, arg)
    return ic_one

def ib_two(self: "pdb.Pdb", arg):
    from waivek.ic import ib
    assert self.curframe
    val = eval(arg, self.curframe.f_globals, self.curframe.f_locals)
    ib(val)

def make_ib_one_arg(self: "pdb.Pdb"):
    def ib_one(arg):
        ib_two(self, arg)
    return ib_one

def print_error_information_from_pdb(self: "pdb.Pdb", error: Exception):
    # frame = self.curframe
    # assert frame
    if not self.curframe:
        raise ValueError('No frame selected')
    print_error_information(error, self.curframe)

@contextmanager
def handler():
    from json import JSONDecodeError # takes 0.01s - 0.02s
    import traceback # takes 0.002s, not much but still inlining
    try:
        yield
    except Exception as error:
        if isinstance(error, JSONDecodeError):
            handle_json_decode_error(error)
        if type(error).__name__ == 'bdb.BdbQuit':
            pass
        else:
            # pdb.post_mortem(error.__traceback__); return
            import pdb

            caller_file = sys._getframe(2).f_code.co_filename

            Pdb = pdb.Pdb()
            Pdb.reset()

            # CUSTOMIZATION 2: Move the debugger to the frame where the error occurred within the file from which the program was run, instead of the frame where the error was raised
            frames = [ frame for frame, _ in traceback.walk_tb(error.__traceback__) ]
            # needle_frame = next(frame for frame in reversed(frames) if frame.f_code.co_filename == __file__)
            needle_frame = next(frame for frame in reversed(frames) if frame.f_code.co_filename == caller_file)
            Pdb.setup(f=None, tb=error.__traceback__) # NOTE[1/1]: Do not do `Pdb.setup(f=needle_frame, tb=error.__traceback__)` as it creates new frames or something

            _select_frame_silent(Pdb, frames.index(needle_frame))

            # CUSTOMIZATION 3: Add `x` and `y` commands for moving up and down the stack in a customized way, and `z` command for printing variables
            Pdb.do_x = make_x_one(Pdb, error)      # pyright:ignore[reportAttributeAccessIssue]
            Pdb.do_y = make_y_one(Pdb, error)      # pyright:ignore[reportAttributeAccessIssue]
            Pdb.do_z = make_z_zero_arg(Pdb, error) # pyright:ignore[reportAttributeAccessIssue]
            Pdb.do_v = make_v_zero_arg(Pdb, error) # pyright:ignore[reportAttributeAccessIssue]

            # CUSTOMIZATION 1: Add `ic` and `ib` aliases for exploration
            Pdb.do_ic = make_ic_one_arg(Pdb)       # pyright:ignore[reportAttributeAccessIssue]
            Pdb.do_ib = make_ib_one_arg(Pdb)       # pyright:ignore[reportAttributeAccessIssue]

            # CUSTOMIZATION 4: Nicer stacktrace
            print_error_information_from_pdb(Pdb, error)
            Pdb._cmdloop()

def select_frame_for_file(frames: List[FrameType], target_file: str) -> Optional[FrameType]:
    for frame in reversed(frames):
        if frame.f_code.co_filename == target_file:
            return frame
    return None

def raise_simple_json_decode_error():
    import json
    string = ''
    json.loads(string)
    raise json.JSONDecodeError('Expecting value', '', 0)

def main():
    # files:
    #   [1] json_decode_error.py

    raise_simple_json_decode_error()
    # raise Exception('This is an error', 1)

if __name__ == "__main__":
    with handler():
        main()
# run.vim: vert term python waivek/__init__.py
