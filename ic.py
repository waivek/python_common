
# Brief:
# 1. Timing things
# 2. Printing Error messages
# 3. Printing variables
# 4. Printing dictionaries and tables
# 5. Autocomplete
# 6. Coloring Strings

from common import Timer, print_error_information, print_dict, truncate, Date, make_string_green

timer = Timer()

import inspect
import os
import os.path
import types


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
    import gc

    frame_info = inspect.stack()[frame_index]
    frame = frame_info[0]

    fname = frame_info.function
    function_object = gc.get_referrers(frame.f_code)[0]
    keys = inspect.getfullargspec(function_object).args

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

# tuple_table:
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
    return type(table) == dict

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
        import dateutil.parser
        table = Table()
        table.parse({
            "ist": value.string,
            "utc": value.dt.astimezone(dateutil.tz.gettz("UTC")).isoformat()[:-6],
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
    import pdb
    stack = inspect.stack()
    frames = [ frame_info.frame for frame_info in stack ]
    modules = [ inspect.getmodule(frame) for frame in frames ]
    return any(module == pdb for module in modules)

def ic(*values):
    # import sys
    # in_pdb = sys.gettrace() != None
    in_pdb = pdb_check()

    if not values:
        if in_pdb:
            print(make_string_green("IN (pdb)."))
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
        s = make_string_green(str(value))
        print(f"{arg_string}: {s}")

__all__ = [ "ic", "ib" ]

class Table:
    def __init__(self):
        self.gutter = '  '
        # self.separator = '  '
        self.separator = ' : '
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
            return [ "key", "value" ], items
        elif is_multi_dict_table(table):
            keys = table[0].keys()
            L = [ tuple(D[key] for key in keys) for D in table ]
            return keys, L
        return None

    def get_column_tuples(self, headers, tuple_table):
        def get_column_just(column):
            is_numeric = all(type(cell) in [int, float] for cell in column)
            return str.rjust if is_numeric else str.ljust

        column_count = len(tuple_table[0])
        columns = [ list(row[i] for row in tuple_table) for i in range(column_count) ]
        column_tuples = [ ( max(len(str(cell)) for cell in column), get_column_just(column) ) for column in columns  ]
        if headers:
            column_tuples = [ (max(width, len(header)), just) for header, (width, just) in zip(headers, column_tuples) ]
        return column_tuples

    def to_string(self):
        def fmt(cells, column_tuples):
            S = self.separator
            G = self.gutter
            return G + S.join(just(str(cell), width) for cell, (width, just) in zip(cells, column_tuples))

        headers, tuple_table = self.normalize_table()
        column_tuples = self.get_column_tuples(headers, tuple_table)

        header_lines = [ "", fmt(headers, column_tuples), "" ] if headers else [ "" ]
        row_lines = [ fmt(row, column_tuples) for row in tuple_table ]
        table_string = "\n".join(header_lines+row_lines)
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
    print()

    breakpoint()
    # }}}

# IntelliJ: Replace VCS Buttons
# IntelliJ: Button at Top
# IntelliJ: Go To Line
# IntelliJ: Breakpoint Functionality
# IntelliJ: Structure Functionality

# Vim: https://github.com/jeetsukumaran/vim-pythonsense#stock-vim-vs-pythonsense-motions
# Vim: https://github.com/wellle/context.vim
# Vim: Jedi Intellisense
# Vim: gd for class
# Vim: go to end of function 
def main():
    # _visit_after_children: C:\Users\vivek\AppData\Roaming\Python\Python37\site-packages\asttokens\mark_tokens.py :63
    pass

if __name__ == "__main__":
    try:
        main()
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
