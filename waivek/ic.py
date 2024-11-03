# See `IMPORT INFORMATION` section in ic()

# Brief:
# 1. Timing things
# 2. Printing Error messages
# 3. Printing variables
# 4. Printing dictionaries and tables
# 5. Autocomplete
# 6. Coloring Strings <externalized to color.py>

from waivek.timer import Timer
timer = Timer()

from waivek.common import print_dict, Date
from waivek.truncate import truncate, get_display_length
from waivek.color import Code

import sys
import os
import os.path
import types
import re

# TextDoc.docroutine

# docroutine {{{
def classname(object, modname):
    """Get a class name and qualify it with a module name if necessary."""
    name = object.__name__
    if object.__module__ != modname:
        name = object.__module__ + '.' + name
    return name

def getdoc(object):
    import re
    import inspect
    """Get the doc string or comments for an object."""
    result = inspect.getdoc(object) or inspect.getcomments(object)
    return result and re.sub('^ *\n', '', result.rstrip()) or ''

def indent(text, prefix='    '):
    """Indent text by prepending a given prefix to each line."""
    if not text:
        return ''
    lines = [prefix + line for line in text.split('\n')]
    if lines:
        lines[-1] = lines[-1].rstrip()
    return '\n'.join(lines)

def _is_bound_method(fn):
    import inspect
    if inspect.ismethod(fn):
        return True
    if inspect.isbuiltin(fn):
        self = getattr(fn, '__self__', None)
        return not (inspect.ismodule(self) or (self is None))
    return False

def docroutine(object, name=None, mod=None, cl=None):
    import inspect
    """Produce text documentation for a function or method object."""
    realname = object.__name__
    name = name or realname
    note = ''
    skipdocs = 0
    if _is_bound_method(object):
        imclass = object.__self__.__class__
        if cl:
            if imclass is not cl:
                note = ' from ' + classname(imclass, mod)
        else:
            if object.__self__ is not None:
                note = ' method of %s instance' % classname(
                    object.__self__.__class__, mod)
            else:
                note = ' unbound %s method' % classname(imclass, mod)

    if name == realname:
        title = realname
    else:
        if cl and realname in cl.__dict__ and cl.__dict__[realname] is object:
            skipdocs = 1
        title = name + ' = ' + realname
        
    argspec = None

    if inspect.isroutine(object):
        try:
            signature = inspect.signature(object)
        except (ValueError, TypeError):
            signature = None
        if signature:
            argspec = str(signature)
            if realname == '<lambda>':
                title = name + ' lambda '
                # XXX lambda's won't usually have func_annotations['return']
                # since the syntax doesn't support, but it is possible.
                # So removing parentheses isn't truly safe.
                argspec = argspec[1:-1]  # remove parentheses
    if not argspec:
        argspec = '(...)'
    decl = title + argspec + note

    if skipdocs:
        return decl + '\n'
    else:
        doc = getdoc(object) or ''
        return '\n' + decl + '\n' + (doc and indent(doc).rstrip() + '\n')
    # }}}

def sig(frame_index=1):
    import inspect

    frame_stack = inspect.stack()
    frame_info = frame_stack[frame_index]
    frame = frame_info[0]

    fname = frame_info.function

    # Works in Python 3.8 but not 3.10
    # import gc
    # function_object = gc.get_referrers(frame.f_code)[0]

    if fname != "<module>":
        function_object = frame.f_globals[fname]
        keys = inspect.getfullargspec(function_object).args
    else:
        keys = []

    # fname = frame_info.function
    # function_object = eval(fname)
    # keys = inspect.getfullargspec(function_object).args

    D = frame.f_locals
    values = [ D[key] for key in keys ]
    parameter_string = "(" + ", ".join(repr(value) for value in values) + ")"
    value_string = "{function_name}{parameters}".format(function_name=fname, parameters=parameter_string)

    return value_string

def get_context(callFrame=None):
    import inspect
    callFrame = callFrame if callFrame else sys._getframe().f_back
    assert callFrame
    frameInfo = inspect.getframeinfo(callFrame)
    # lineNumber = frameInfo.lineno
    lineNumber = callFrame.f_lineno
    # parentFunction = frameInfo.function
    filename = os.path.basename(frameInfo.filename)
    # if parentFunction != '<module>':
    #     parentFunction = '%s()' % parentFunction
    signature = sig(3)
    return '%s:%s %s' % (filename, lineNumber, signature)

def is_function(value):
    function_types = [
        types.BuiltinFunctionType,
        types.FunctionType,
        types.MethodDescriptorType,
        types.MethodType,
    ]
    result = type(value) in function_types
    return result

#  tuple_table:
#     1. [ tuple | list ]
#     2. all sublists are identical in length
# single_dict_table:
#     1. type == dict
# multi_dict_table:
#     1. [ dict ]
#     2. all dicts are identical in keys()

def is_tuple_table(table):
    if type(table) != list:
        return False
    types = list(set(type(row) for row in table))
    if len(types) != 1:
        return False
    common_type = types[0]
    return common_type in [ tuple, list ]

def is_single_dict_table(table):
    # we add items check so that Date class doesn’t pass
    return type(table) == dict or (hasattr(table, '__dict__') and hasattr(table, 'items'))

def is_multi_dict_table(table):
    if type(table) != list:
        return False
    if any(type(row) != dict for row in table):
        return False
    from itertools import groupby
    unique_key_combinations = list(groupby([ D.keys() for D in table ]))
    return len(unique_key_combinations) == 1

def is_db_table(table):
    if type(table) != list:
        return False
    from waivek.dbutils import get_sqlite3
    sqlite3 = get_sqlite3()
    boolean = all(type(row) == sqlite3.Row for row in table) 
    return boolean

def table_friendly(table):
    return is_tuple_table(table) or is_single_dict_table(table) or is_multi_dict_table(table) or is_db_table(table)

def get_max_width_and_height():
    in_terminal = sys.stdout.isatty()
    if in_terminal:
        return os.get_terminal_size()
    else:
        return (200, 200)

def max_lines():
    in_terminal = sys.stdout.isatty()
    if in_terminal:
        return os.get_terminal_size().lines
    else:
        return 200

# is_tuple_table, is_single_dict_table, is_multi_dict_table
def list_fmt(L):
    max_width, max_height = get_max_width_and_height()
    max_height = int(max_lines() / 2)
    half_height = int(max_height / 2)
    list_length = len(L)
    space_count = len(str(list_length)) + 2
    max_width = max_width - space_count - 5
    if len(str(L)) < max_width:
        return str(L)
    elif list_length > max_height:
        lines = []
        for i in range(0, half_height):
            L_string = truncate(str(L[i]), max_width)
            padded_i = f"[{i}]".rjust(space_count)
            lines.append(f"{padded_i}: {L_string}")
        lines.append(f"{' ' * space_count}  ...")
        for i in range(list_length - half_height, list_length):
            L_string = truncate(str(L[i]), max_width)
            padded_i = f"[{i}]".rjust(space_count)
            lines.append(f"{padded_i}: {L_string}")
        return "\n".join(lines)
    else:
        lines = []
        for i in range(0, list_length):
            L_string = truncate(str(L[i]), max_width)
            padded_i = f"[{i}]".rjust(space_count)
            lines.append(f"{padded_i}: {L_string}")
        return "\n".join(lines)

def describe_function(arg):
    name = getattr(arg, '__name__', None)
    doc_string = docroutine(arg, name)
    return doc_string

def ic_one(value):
    if table_friendly(value):
        table = Table()
        if is_tuple_table(value) or is_multi_dict_table(value):
            for row in value:
                table.row(row)
        elif is_db_table(value):
            for row in value:
                table.row(dict(row))
        else:
            table.parse(value)
        return str(table)
    if type(value) == list:
        return list_fmt(value)
    if type(value) == Date:
        # import dateutil.parser
        from datetime import timezone
        table = Table()
        table.parse({
            "ist": value.string,
            "utc": value.dt.astimezone(timezone.utc).isoformat()[:-6],
            "epoch": value.epoch,
            "relative": value.timeago()
        })
        return str(table)
    if is_function(value):
        doc_string = describe_function(value)
        return doc_string
    if type(value) == types.ModuleType:
        return ic_one({
            key: getattr(value, key) .__doc__.strip().split("\n")[0] if getattr(value, key).__doc__ else "No __doc__"
            for key in dir(value) if is_function(getattr(value, key)) and not key.startswith("_") 
        })
    return str(value)

def ib(obj):
    def custom_str(v):
        if is_function(v):
            return v.__doc__.strip().split("\n")[0] if v.__doc__ else "No __doc__"
        else:
            return truncate(str(v), 160)
    keys = [ key for key in dir(obj) if not key.startswith("__") ]

    keys.sort(key=lambda key: not is_function(getattr(obj, key)))
    D = { key : custom_str(getattr(obj, key)) for key in keys }
    print_dict(D)

def inspect_dot_stack():
    frame_index = 1
    frames = []
    while True:
        try:
            frame = sys._getframe(frame_index)
        except ValueError: 
            break
        frames.append(frame)
        frame_index = frame_index + 1
    return frames

def pdb_check():
    # import inspect
    # stack = inspect.stack() # Takes 300 ms
    # frames = [ frame_info.frame for frame_info in stack ]

    frames = inspect_dot_stack()
    frame_names = [ frame.f_globals['__name__'] for frame in frames ]
    if 'pdb' in frame_names or 'pydevd' in frame_names:
        return True
    else:
        return False
    # modules = [ inspect.getmodule(frame) for frame in frames ]
    # return pdb in modules

path_to_lines = {}
def frame_to_line(frame):
    # Implementation 1
    # ================
    # import linecache
    # linecache.getline(frame.f_code.co_filename, frame.f_lineno).strip()
    path = frame.f_code.co_filename
    if path not in path_to_lines:
        with open(path, "r") as f:
            lines = f.readlines()
        path_to_lines[path] = lines
    lines = path_to_lines[path]
    line = lines[frame.f_lineno-1]
    return line

def ic(*values):
    # IMPORT INFORMATION
    # ==================
    #
    # ast     : Only import ast for instances like ic(1, 2) or ic(foo(a), [1,2,3]) and not of ic(1) ic(2) which is most common use case
    # inspect : Only import for ic() / ic(function) / ic(module) / sig()

    in_pdb = pdb_check()

    if not values:
        if in_pdb:
            print(Code.GREEN + "IN (pdb).")
            return
        callFrame = sys._getframe().f_back
        context_string = get_context(callFrame)
        print(context_string)
        return

    x = values[0]
    if len(values) == 1 and ic_one(x) != str(x):
        # print("A")
        print(ic_one(x))
        return

    if in_pdb:
        for value in values:
            print(str(value))
        return

    # Implementation 3:
    # =================
    frame = sys._getframe(1)
    line = frame_to_line(frame).strip()
    if len(values) == 1:
        print(f"{line[3:-1]}: {Code.LIGHTCYAN_EX+values[0]}")
    else:
        import ast
        stmt = ast.parse(line).body[0]
        node = stmt.value

        for arg, value in zip(node.args, values):
            print(f"{ast.unparse(arg)}: {Code.LIGHTCYAN_EX+value}")

__all__ = [ "ic", "ib" ]

def len_without_ansi_codes(s: str):
    # Regex to match ANSI escape sequences
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')

    # Remove ANSI codes
    clean_string = ansi_escape.sub('', s)
    # Print the length of the cleaned string
    return len(clean_string)

# def len_without_ansi_codes(s):
#     import re
#     ansi_codes = [ '\x1b[30m', '\x1b[31m', '\x1b[32m', '\x1b[33m', '\x1b[34m', '\x1b[35m', '\x1b[36m', '\x1b[37m', '\x1b[90m', '\x1b[91m', '\x1b[92m', '\x1b[93m', '\x1b[94m', '\x1b[95m', '\x1b[96m', '\x1b[97m' ]
#     ansi_codes_joined = "".join(ansi_codes)
#     return len(re.sub(f'[{ansi_codes_joined}]', '', s))

def log(dictionaries):
    from waivek.db import db_init
    from time import time
    import json
    connection = db_init("errors/ic.db")
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS errors (epoch INTEGER NOT NULL, list_json TEXT NOT NULL UNIQUE ON CONFLICT IGNORE);")
    list_json = json.dumps(dictionaries)
    epoch = int(time())
    cursor.execute("INSERT INTO errors (epoch, list_json) VALUES (?, ?);", (epoch, list_json))
    connection.commit()

def save_ic_table_error(dictionaries):
    from datetime import datetime
    from waivek.reltools import write
    dt = datetime.now()
    filename = f"{dt:%y%m%d-%Hh%Mm%Ss}.json"
    path = os.path.abspath(os.path.expanduser(f'~/Documents/Python/ic-test-manual/{filename}'))
    write(dictionaries, filename)

def ljust_display(s, width):
    fill = " "
    display_length = get_display_length(s)
    if display_length < width:
        return s + fill * (width - display_length)
    else:
        return s

def rjust_display(s, width):
    fill = " "
    display_length = get_display_length(s)
    if display_length < width:
        return fill * (width - display_length) + s
    else:
        return s

class Table:
    # Why we can’t use columnar
    #
    # 1. No option for separator only between columns. Any separator you choose is also part of the border
    # 2. 150ms import time vanilla 
    def __init__(self):
        self.gutter = '  '
        self.separator = '  '
        self.table = []

    def row(self, *args):
        if len(args) == 1:
            L = args[0]
        else:
            L = list(args)
        self.table.append(L)

    def parse(self, D):
        self.table = D

    def normalize_table(self):
        table = self.table
        if is_tuple_table(table):
            L = [ tuple(sublist) for sublist in table ]
            return [], L
        elif is_single_dict_table(table):
            assert hasattr(table, 'items')
            items = list(table.items()) # pyright:ignore[reportAttributeAccessIssue]
            return [ "KEY", "VALUE" ], items
        elif is_db_table(table): # Transform to multi_dict_table, DRY Violated
            multi_dict_table = [ dict(row) for row in table ]
            keys = multi_dict_table[0].keys()
            L = [ tuple(D[key] for key in keys) for D in multi_dict_table ]
            return keys, L
        elif is_multi_dict_table(table):
            keys = table[0].keys()
            L = [ tuple(D[key] for key in keys) for D in table ]
            return keys, L

        return None

    def get_column_tuples(self, headers, tuple_table):
        def get_column_just(column):
            is_numeric = all(type(cell) in [int, float] for cell in column)
            return rjust_display if is_numeric else ljust_display
        def get_width(cell):
            # Handles multi-line strings
            cell_str = str(cell)
            val = max(get_display_length(line) for line in cell_str.split("\n")) # get_display_length
            return val
        def distribute(initial_lengths, terminal_length):
            final_lengths = [ 0 for _ in initial_lengths ]
            total_length = 0
            while total_length != terminal_length:
                all_lengths_satisfied = all([ initial_length == final_length for initial_length, final_length in zip(initial_lengths, final_lengths) ])
                if all_lengths_satisfied:
                    break
                for i, length in enumerate(initial_lengths):
                    if final_lengths[i] == initial_lengths[i]:
                        continue
                    final_lengths[i] = final_lengths[i] + 1
                    total_length += 1
                    if total_length == terminal_length:
                        break
            return final_lengths

        column_count = len(tuple_table[0])
        columns = [ list(row[i] for row in tuple_table) for i in range(column_count) ]
        column_tuples = [ ( max(get_width(cell) for cell in column), get_column_just(column) ) for column in columns  ]
        if headers:
            column_tuples = [ (max(width, len(header)), just) for header, (width, just) in zip(headers, column_tuples) ]

        # Distribute Column Widths given terminal size
        initial_widths = [ width for width, _ in column_tuples ]
        
        terminal_width, _ = get_max_width_and_height()
        gutter_width = len(self.gutter) * 2
        separator_width = len(self.separator) * (column_count-1)
        column_width_total = terminal_width - gutter_width - separator_width
        final_widths = distribute(initial_widths, column_width_total)
        for i, (width, just) in enumerate(column_tuples):
            column_tuples[i] = (final_widths[i], just)
        return column_tuples

    # wrap_box {{{
    def wrap_box(self, item, width, height, just):
        # Purpose: Handle truncate, wrap, newline, padding
        # If there is a newline, avoid truncate() probably and truncate on line
        # Make sure returned result is padded correctly and all lines have the width specified
        # If >1 line, all lines HAVE to have the same width
        #
        # For really big dicts and lists do two things 
        # 1.1) color code keys/top-level commas in the box so that it is easy to parse
        # 1.2) give alternating colors to top-level items so that it is easy to parse
        # 2) use as much horizontal space possible
        # 
        # Handle color codes in wrapped lienes
        # 1) Right now color codes are counted in the length of the file (this is in `Table.get_width` and `textwrap.wrap`)
        # 2) I'm pretty sure color codes spill over to next cell. Illusion only works as long as colored-block is also the last block
        #
        # Ideally ic should not insert any new color on it’s on. Input’s should come in colored and ic resets multi-line color blocks appropriately
        # ic should also not replace a "\n" with a r"\n". This should also be done before ic()
        #
        # There is something very appealing about ic printing by default in black-and-white AS IS
        #
        # truncate() also has to take into account length of ANSI escape characters
        #

        pass

    # }}}

    def to_string(self):

        def fmt(cells, column_tuples):
            S = self.separator
            G = self.gutter
            all_strings_are_single_line = all("\n" not in str(cell) for cell in cells)
            if all_strings_are_single_line:
                return G + S.join(just(truncate(str(cell), width), width) for cell, (width, just) in zip(cells, column_tuples))
            else:
                cells = [ str(cell) for cell in cells ]
                largest_height = max(len(cell.split("\n")) for cell in cells)
                v_pad_cells = [ v_pad(cell.split("\n"), largest_height) for cell in cells ]
                return_lines = []
                for i in range(largest_height):
                    parts = [ v_pad_cell[i] for v_pad_cell in v_pad_cells ]
                    parts = [ just(truncate(part, width), width) for part, (width, just) in zip(parts, column_tuples) ] 
                    return_lines.append(G + S.join(parts))
                return "\n".join(return_lines)

        result = self.normalize_table()
        assert result
        headers, tuple_table = result
        column_tuples = self.get_column_tuples(headers, tuple_table)

        header_lines = [ "", fmt(headers, column_tuples), "" ] if headers else [ "" ]
        footer_lines = [ "" ]
        row_lines = [ fmt(row, column_tuples) for row in tuple_table ]
        table_string = "\n".join(header_lines+row_lines+footer_lines)
        return table_string

    def __str__(self):
        return self.to_string()

# test_ic (8 functions) {{{
def data_source_paths():
    T = [ 
        (r"C:\users\vivek\Documents\Python\ic.py:163", r"result = upper / lower"),
        (r"C:\users\vivek\Documents\Python\ic.py:229", r"ic_one(value)"),
        (r"C:\Users\vivek\Desktop\Twitch\coffee-vps\code\twitch_utilities.py:4112", r"ic(st)"),
        (r"C:\Users\vivek\Desktop\Twitch\coffee-vps\code\twitch_utilities.py:4225", r"main()") 
    ]
    return T

def data_source_mixed_dict():
    from datetime import datetime
    D = {
        "epoch": 1641749543,
        100: "hundred",
        "date": datetime.now(),
        "list": [1, 2, 3, 4]
    }
    return D

# Required for error.print_variables_by_frame
def data_source_multiline_long_colored_variables():
    # import pdb
    # tall_string = str(pdb.__doc__)
    import textwrap
    from waivek.error import color_D_if_big
    range_count = 100
    numbers = list(range(range_count))
    alphabets = [ "abcdefghijklmnopqrstuvwxyz", "ABCDEFGHIJKLMNOPQRSTUVWXYZ" ]
    select_sql_extra_space = r"""
    SELECT datetime(created_at, "+"||offset||" seconds") clip_utc FROM 
        (SELECT id, created_at FROM videos)
        INNER JOIN
        (SELECT slug, "vod.id", "vod.offset" offset FROM kraken_clips)
    ON id="vod.id";
    """
    select_sql = textwrap.dedent(select_sql_extra_space).strip()

    # local_D = locals()
    # mystuff = "\n".join(textwrap.wrap(color_D_if_big(local_D), 80))
    from rich import ansi
    decoder = ansi.AnsiDecoder()

    # timer.start("import Table")
    # from rich.console import Console
    # from rich.table import Table
    # timer.print("import Table")
    # table = Table(title="two-column display")
    # mystuff = next(decoder.decode(color_D_if_big(locals())))
    # table.add_column("key")
    # table.add_column("value")
    # table.add_column("type")
    # for key, value in locals().items():
    #     if key == "mystuff":
    #         table.add_row(key, value, str(type(value)))
    #     else:
    #         table.add_row(key, str(value), str(type(value)))
    # console = Console()
    # console.print(table)
    # # r_print(local_D["mystuff"])

    # table = Table()
    # for key, value in locals().items():
    #     if key == 'table':
    #         continue
    #     table.row(key, str(value), str(type(value)))
    # print(table)

def single_dict_table():
    D = data_source_mixed_dict()
    return D

def multi_dict_table():
    T = data_source_paths()
    return [ { "path": path, "line": line } for path, line in T ]

def tuple_table():
    return data_source_paths()

def fn_call():
    return 'Called Result'

def joined_string(prefix, postfix, D, call_result, da):
    return " | ".join([ prefix, postfix, str(D), call_result, str(da)])

def test_ic():
    table1 = tuple_table()
    table2 = multi_dict_table()
    table3 = single_dict_table()

    ic(table1)
    ic(table2)
    ic(table3)
    ic(os.path)
    ic(Date.now())

    print()

    ret = "Hello, World"
    before = 'prefix '
    ic()
    ic(joined_string(before, '!', {'cat': 'dog'}, fn_call(), Date.now()))
    ic(ret == before)
    ic_locals = locals()
    ic_locals = { str(key).strip(): str(value).strip() for key, value in ic_locals.items() }
    ic(ic_locals)
    print()
    # }}}

# IntelliJ: Replace VCS Buttons
# IntelliJ: Button at Top
# IntelliJ: Go To Line
# IntelliJ: Breakpoint Functionality
# IntelliJ: Structure Functionality

# [DONE] Vim: https://github.com/jeetsukumaran/vim-pythonsense#stock-vim-vs-pythonsense-motions
# [DONE] Vim: https://github.com/wellle/context.vim
# [DONE] Vim: Jedi Intellisense
# [DONE] Vim: gd for class
# [DONE] Vim: go to end of function 

def table_print():
    #  data
    #  headers
    #  head = 0
    #  justify = 'l'
    #  wrap_max = 5
    #  max_column_width = None
    #  min_column_width = 5
    #  row_sep = '-'
    #  column_sep = '|'
    #  patterns = []
    #  drop = []
    #  select = []
    #  no_borders = False
    #  terminal_width = None
    from columnar import columnar
    no_top_padding = True
    table = [ list(T) for T in tuple_table() ]
    table[0][1] = Code.GREEN + table[0][1]
    result = columnar(table, row_sep="", column_sep="...")
    if no_top_padding:
        result = "\n".join(result.split("\n")[1:])

    print("\n-- START --")
    print(result)
    print("-- FINISH --")

def v_pad(list_or_string, line_count=1):

    L = [ list_or_string ] if type(list_or_string) == str else list_or_string
    max_length = max(len(s) for s in L)
    list_height = len(L)
    if list_height <= line_count:
        blank_line_count = line_count - list_height
        result_lines = L + [ " " * max_length ] * blank_line_count
    else:
        top_end = int(line_count/2)
        bot_start = list_height - int(line_count/2) + 1
        slice_L = L[0:top_end] + [ "..." ] + L[bot_start:]
        if len(slice_L) != line_count:
            print(Code.RED +  "(error) v_pad(list_string, line_count)")
            print(Code.RED + f"....... len(slice_L): {len(slice_L)}")
            print(Code.RED + f"....... line_count  : {line_count}")
            breakpoint()
        result_lines = slice_L
    return result_lines

def wrap_test():
    # multi-line variable in table support
    # use case: C:\Users\vivek\Desktop\Twitch\coffee-vps\code\err_test.py
    import textwrap
    import pdb
    target_width = 70
    # target_height = 10
    range_count = 100

    list_string = str(list(range(range_count)))
    # list_string = "".join(str(i) for i in range(range_count))

    small_string = f"Numbers till {range_count}"

    tall_string = str(pdb.__doc__).strip()

    list_parts = textwrap.wrap(list_string, target_width)
    list_parts = [ list_part.ljust(target_width) for list_part in list_parts ]
    target_height = len(list_parts)
    small_parts = v_pad(small_string, target_height)
    tall_parts = v_pad(tall_string.split("\n"), target_height)

    single_toggle = True
    for small_part, list_part, tall_part in zip(small_parts, list_parts, tall_parts):
        if single_toggle:
            print(small_part + " ... " + list_part + " ... " + tall_part)
            single_toggle = False
        else:
            print(small_part + "     " + list_part + "     " + tall_part)

def foo(x, y):
    return x + y

def baz(string):
    return string.upper()

def get_args(*values):
    import executing
    # import inspect
    import ast
    stack = inspect_dot_stack()
    frame = sys._getframe(1)
    
    node = executing.Source.executing(frame).node
    print(ast.unparse(node))
    import inspect
    import linecache
    source = inspect.getsource(frame)
    mod = ast.parse(''.join(linecache.getlines(frame.f_code.co_filename)))
    breakpoint()
    # nodes = ast.parse(source)
    # for node in ast.walk(nodes):
    #     try:
    #         if node.value.func.id == 'get_args':
    #             print("---")
    #             print(ast.unparse(node))
    #     except:
    #         pass

    print(frame.f_lineno)
    # print(ast.unparse(nodes))
    print()

def error_1():
    from waivek.db import db_init
    import json
    connection = db_init("errors/ic.db")
    cursor = connection.cursor()
    dictionaries = [ dict(row) for row in cursor.execute("SELECT * FROM errors") ]
    json_strings = [ D["list_json"] for D in dictionaries ]
    dictionaries = [ json.loads(json_string) for json_string in json_strings ]
    for D in dictionaries:
        ic(D)

def error_2():
    from waivek import read
    D = read("ic-test-manual/221015.json")
    ic(D)

def get_small_colored_table() -> list:
    ansi_red = "\x1b[31m"
    ansi_reset_all = "\x1b[0m"
    row1 = [ "1", "2", "3", "4", "5" ]
    row2 = [ "6", "7", ansi_red + "8" + ansi_reset_all, "9", "10" ]
    return [ row1, row2 ]

def main():
    table = get_small_colored_table()
    ic(table)
    return

    variable = 20
    my_string = "3"
    print(("=" + "\x1b[96m").join(f"{my_string = }".split("=", 1)) + "\x1b[39m")
    return
    from waivek.data import Countries
    ic(Countries)
    return
    error_2() # Doesn’t Work / Reproduce the error
    return 
    save_ic_table_error([])
    return
    # ic(1)
    string = '1'
    # ic(string)
    # ic(foo(1,2), 3)
    # get_args(foo(1, 2), 'Three')
    return
    string = 'Hey'
    get_args(baz(string))
    return
    # _visit_after_children: C:\Users\vivek\AppData\Roaming\Python\Python37\site-packages\asttokens\mark_tokens.py :63
    # test_ic()
    # normal_len = len(s)
    # ic(calc_len, normal_len)
    # # Required for error.print_variables_by_frame

# main()

timer.no_print = False

if __name__ == "__main__":

    from waivek.error import handler
    with handler():
        main()
