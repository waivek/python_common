


# Brief:
# 1. Timing things
# 2. Printing Error messages
# 3. Printing variables
# 4. Printing dictionaries and tables
# 5. Autocomplete
# 6. Coloring Strings

from timer import Timer
timer = Timer()

from common import print_error_information, print_dict, truncate, Date
from color import Code


import inspect # Takes 110 ms main bottleneck, see usecases at ./inspect_use_cases.txt
import os
import os.path
import types

global_breakpoint_time = False

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
    if inspect.ismethod(fn):
        return True
    if inspect.isbuiltin(fn):
        self = getattr(fn, '__self__', None)
        return not (inspect.ismodule(self) or (self is None))
    return False

def docroutine(object, name=None, mod=None, cl=None):
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
    callFrame = callFrame if callFrame else inspect.currentframe().f_back
    frameInfo = inspect.getframeinfo(callFrame)
    lineNumber = frameInfo.lineno
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

def table_friendly(table):
    return is_tuple_table(table) or is_single_dict_table(table) or is_multi_dict_table(table)

# is_tuple_table, is_single_dict_table, is_multi_dict_table
def list_fmt(L):
    max_width, max_height = os.get_terminal_size()
    max_height = int(os.get_terminal_size().lines / 2)
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

def pdb_check():
    stack = inspect.stack() # Takes 300 ms
    frames = [ frame_info.frame for frame_info in stack ]
    frame_names = [ frame.f_globals['__name__'] for frame in frames ]
    if 'pdb' in frame_names or 'pydevd' in frame_names:
        return True
    else:
        return False
    # modules = [ inspect.getmodule(frame) for frame in frames ]
    # return pdb in modules

def ic(*values):
    in_pdb = pdb_check() # Takes 300 ms

    if not values:
        if in_pdb:
            print(Code.GREEN + "IN (pdb).")
            return
        callFrame = inspect.currentframe().f_back
        context_string = get_context(callFrame)
        print(context_string)
        return

    x = values[0]
    if len(values) == 1 and ic_one(x) != str(x):
        print(ic_one(x))
        return

    if in_pdb:
        for value in values:
            print(str(value))
        return
    
    import executing
    callFrame = inspect.currentframe().f_back
    callNode = executing.Source.executing(callFrame).node
    for_frame = executing.Source.for_frame(callFrame)
    # asttokens() - 250ms Delay
    arg_strings = [ for_frame.asttokens().get_text(arg) for arg in callNode.args ]
    pairs = list(zip(arg_strings, values))
    for arg_string, value in pairs:
        s = Code.GREEN + value
        print(f"{arg_string}: {s}")

__all__ = [ "ic", "ib" ]


def len_without_ansi_codes(s):
    import re
    ansi_codes = [ '\x1b[30m', '\x1b[31m', '\x1b[32m', '\x1b[33m', '\x1b[34m', '\x1b[35m', '\x1b[36m', '\x1b[37m', '\x1b[90m', '\x1b[91m', '\x1b[92m', '\x1b[93m', '\x1b[94m', '\x1b[95m', '\x1b[96m', '\x1b[97m' ]
    ansi_codes_joined = "".join(ansi_codes)
    return len(re.sub(f'[{ansi_codes_joined}]', '', s))

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
            items = list(table.items())
            return [ "KEY", "VALUE" ], items
        elif is_multi_dict_table(table):
            keys = table[0].keys()
            L = [ tuple(D[key] for key in keys) for D in table ]
            return keys, L
        return None

    def get_column_tuples(self, headers, tuple_table):
        def get_column_just(column):
            is_numeric = all(type(cell) in [int, float] for cell in column)
            return str.rjust if is_numeric else str.ljust
        def get_width(cell):
            # Handles multi-line strings
            cell_str = str(cell)
            # return max(len_without_ansi_codes(line) for line in cell_str.split("\n"))
            return max(len(line) for line in cell_str.split("\n"))

        column_count = len(tuple_table[0])
        columns = [ list(row[i] for row in tuple_table) for i in range(column_count) ]
        column_tuples = [ ( max(get_width(cell) for cell in column), get_column_just(column) ) for column in columns  ]
        if headers:
            column_tuples = [ (max(width, len(header)), just) for header, (width, just) in zip(headers, column_tuples) ]

        # Distribute Column Widths given terminal size
        initial_widths = [ width for width, _ in column_tuples ]
        terminal_width, _ = os.get_terminal_size()
        gutter_width = len(self.gutter) * 2
        separator_width = len(self.separator) * (column_count-1)
        column_width_total = terminal_width - gutter_width - separator_width
        min_column_width = int(column_width_total / column_count)
        small_indices = [ i for i, width in enumerate(initial_widths) if width <= min_column_width ]
        big_indices = [ i for i, width in enumerate(initial_widths) if width > min_column_width ]
        if len(big_indices) == 0:
            return column_tuples
        small_width_total = sum(width for width in initial_widths if width <= min_column_width)
        remaining_width_total = column_width_total - small_width_total
        big_width = int(remaining_width_total / len(big_indices))
        remaining_width_total = remaining_width_total - big_width * len(big_indices)
        final_big_width = big_width + remaining_width_total
        for i in big_indices:
            _, just = column_tuples[i]
            column_tuples[i] = (big_width, just)
            if i == len(big_indices)-1:
                column_tuples[i] = (final_big_width, just)

        final_widths = [ width for width, _ in column_tuples ]
        calc_total_width = gutter_width + separator_width + sum(final_widths)
        if calc_total_width != terminal_width:
            print(Code.RED +  "calc_total_width != terminal_width")
            print(Code.RED + f"           ({calc_total_width}) !=          ({terminal_width})")
            print(f"Initial Widths                  : {initial_widths}")
            print(f"Column Width All                : {column_width_total}")
            print(f"Minimum Column Width            : {min_column_width}")
            print(f"Final  Widths                   : {final_widths}")
            breakpoint()
        return column_tuples

    def wrap_box(item, width, height, just):
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

        headers, tuple_table = self.normalize_table()
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
    from error import color_D_if_big
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


    timer.start("import Table")
    from rich.console import Console
    from rich.table import Table
    timer.print("import Table")
    table = Table(title="two-column display")
    local_D = locals()
    local_D["mystuff"] = list(decoder.decode(color_D_if_big(local_D)))
    breakpoint()
    table.add_column("key")
    table.add_column("value")
    table.add_column("type")
    for key, value in local_D.items():
        table.add_row(key, str(value), str(type(value)))
    console = Console()
    console.print(table)




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
    # global global_breakpoint_time
    # global_breakpoint_time = True
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



def main():
    # _visit_after_children: C:\Users\vivek\AppData\Roaming\Python\Python37\site-packages\asttokens\mark_tokens.py :63
    # test_ic()
    s = Code.GREEN + "HELLO"
    calc_len = len_without_ansi_codes(s)
    normal_len = len(s)
    ic(calc_len, normal_len)

if __name__ == "__main__":
    try:
        # ic()
        # Required for error.print_variables_by_frame
        data_source_multiline_long_colored_variables()
    except Exception as e:
        import bdb
        import pdb
        error = e
        if type(e) == bdb.BdbQuit:
            # Exit Via CTRL-D
            pass
        else:
            print_error_information(e)
            pdb.post_mortem(e.__traceback__)
