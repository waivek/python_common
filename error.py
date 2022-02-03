
import os.path
from color import Code
from timer import Timer
timer = Timer()

from contextlib import contextmanager

def print_error_information(error):
    # C:\Users\vivek\Documents\Python                               -> ~/Documents/Python
    # C:\Users\vivek\AppData\Roaming\Python\Python310\site-packages -> $APPDATA/Python/site-packages
    # C:\Program Files\Python310\Lib\site-packages                  -> 
    import traceback

    tb = error.__traceback__

    print()
    print(Code.RED + repr(error))

    frames = [ frame for frame, _ in traceback.walk_tb(tb) ]

    summaries = traceback.extract_tb(tb)
    pairs = reversed(list(zip(frames, summaries)))
    
    from ic import Table
    table = Table()
    table.gutter = '    '
    table.separator = ' ... '
    for i, (frame, summary) in enumerate(pairs):
        filepath = os.path.relpath(os.path.abspath(summary.filename))
        line_number = summary.lineno
        line = summary.line
        line = Code.GREEN + line if i == 0 else line
        lhs_string = f"{filepath}:{line_number}"
        table.row([lhs_string, line])
    table_string = str(table)
    table_lines = table_string.split("\n")
    table_lines = table_lines[1:]
    table_string = "\n".join(table_lines)
    print(table_string)
    print()

@contextmanager
def handler():
    try:
        yield
    except Exception as e:
        import bdb
        error = e
        if type(e) == bdb.BdbQuit:
            # Exit Via CTRL-D
            pass
        else:
            print_error_information(e)
            import sys
            if True or "ipython" in sys.argv[0]:
                import ipdb
                ipdb.post_mortem(e.__traceback__)
            else:
                import pdb
                pdb.post_mortem(e.__traceback__)

def divide_by_zero():
    upper = 5
    lower = 0
    result = upper / lower
    return result

def level_2():
    return divide_by_zero()

def level_1():
    level_2()

if __name__ == "__main__":
    with handler():
        level_2()
