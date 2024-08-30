# from colorama import init, Fore
# init(convert=True)
from waivek.color import Code

# print_object {{{
def print_object(obj, hidden=False):
    if not hidden:
        keys = [ key for key in dir(obj) if not key.startswith("__") ]
    else:
        keys = dir(obj)

    D = { key : obj.__getattribute__(key) for key in keys }
    print_dict(D)
    # }}}

# print_dict {{{
def print_dict(D):
    from columnar import columnar
    if type(D) != type({}):
        argument_type = str(type(D))
        str_representation = truncate(str(D), 40)
        print_red_line("Please pass a dictionary. Invalid type {arg_type} with str representation {str_rep}".format(
            arg_type=argument_type, str_rep=str_representation))
        return
    data = []
    for key, value in D.items():
        trunc_val = truncate(str(value), 80)
        data.append([key, trunc_val])
    headers = [ "key", "value" ]
    table = columnar(data, headers, no_borders=True)
    print(table)
    # }}}

# print_table {{{
# Assumption: Columns have consistent type
def print_table(dictionaries):
    if len(dictionaries) == 0:
        return
    for D in dictionaries:
        for key in D.keys():
            value = D[key]
            if type(value) != str and type(value) != int and type(value) != float:
                D[key] = str(value)
    # keys = ["basename", "file_read_time", "json_load_time", "total_time"]
    keys = list(dictionaries[0].keys())
    # keys = ["name", "cost", "count"]
    max_length_D = {key:len(key) for key in keys}
    types_D = { key: type(dictionaries[0][key]) for key in keys }
    left_gutter_length = 2
    vertical_padding = 1
    left_gutter_string = " " * left_gutter_length
    column_gap = 2
    separator = " "  * column_gap
    for key in keys:
        max_length = max_length_D[key]
        for D in dictionaries:
            value = D[key]
            if type(value) == str:
                length = len(value)
            if type(value) == int:
                length = len(str(value))
            if type(value) == float:
                length = len("%.2f" % value)
            if max_length < length:
                max_length = length
        max_length_D[key] = max_length

    for i in range(vertical_padding):
        print()
    column_label_items = []
    for key in keys:
        if types_D[key] == str:
            rep = key.ljust(max_length_D[key])
        if types_D[key] == int:
            rep = key.rjust(max_length_D[key])
        if types_D[key] == float:
            rep = key.rjust(max_length_D[key])
        column_label_items.append(rep)
    line = left_gutter_string + separator.join(column_label_items)
    print(line)


    for D in dictionaries:
        line_items = []
        for key in keys:
            max_length = max_length_D[key]
            value = D[key]
            if type(value) == str:
                rep = value.ljust(max_length)
            if type(value) == int:
                rep = str(value).rjust(max_length)
            if type(value) == float:
                rep = ("%.2f" % value).rjust(max_length)
            line_items.append(rep)
        line = left_gutter_string + separator.join(line_items)
        print(line)
    for i in range(vertical_padding):
        print()
# }}}

# head {{{
def head_file(file_contents, preview_lines_count=5):
    lines = file_contents.split("\n")
    preview_lines = lines[0:preview_lines_count]
    return "\n".join(preview_lines)

def head_list(L, preview_lines_count=5):
    preview_L = L[0:preview_lines_count]
    return "\n".join(preview_L)

def head(inp, preview_lines_count=5):
    if type(inp) == list:
        return head_list(inp, preview_lines_count)
    else:
        return head_file(inp, preview_lines_count)
# }}}

# print_red_line, print_green_line {{{
def make_string_green(string):
    # return "{color_code}{string}{reset_code}".format(color_code=Fore.GREEN, string=string, reset_code=Fore.RESET)
    return Code.GREEN + string
def make_string_red(string):
    # return "{color_code}{string}{reset_code}".format(color_code=Fore.RED, string=string, reset_code=Fore.RESET)
    return Code.RED + string
def print_red_line(string):
    print(make_string_red(string))
def print_green_line(string):
    print(make_string_green(string))
    # }}}

# truncate {{{
def truncate(string, length):
    if len(string) < length:
        return string

    middle_string = "..."
    slice_size = int((length-len(middle_string))/2)
    # 80, 38, 38, 3 SUM = 79/80 ONE SPACE AVAILABLE
    # 81, 39, 39, 3 SUM = 81/81 ZERO SPACES AVAILABLE
    even_string_length = length % 2 == 0
    left_end = slice_size
    if even_string_length:
        right_start = slice_size+1
    else:
        right_start = slice_size
    left_slice = string[0:left_end]
    right_slice = string[-right_start:]
    trunc_string = "{left_slice}{middle_string}{right_slice}".format(left_slice=left_slice, middle_string=middle_string, right_slice=right_slice)
    if len(trunc_string) != length:
        print_red_line("ERROR: Could not return a truncated string")
        return "ERROR"
    return trunc_string
# }}}

# abbreviate {{{
def abbreviate(number):
    number_int = int(number)
    number_string = str(number_int)
    number_length = len(str(number_int))
    if number_int < 100:
        return number_string
    first_digit, second_digit, third_digit = number_string[0:3]
    abbreviation_dict = {
         1:  "",  2:  "",  3:  "",
         4: "k",  5: "k",  6: "k",
         7: "m",  8: "m",  9: "m",
        10: "b", 11: "b", 12: "b",
        13: "t", 14: "t", 15: "t"
    }
    letter = abbreviation_dict[number_length]
    if number_length % 3 == 0:
        # first three digits
        abbr_string = f"{first_digit}{second_digit}{third_digit}{letter}"
    if number_length % 3 == 2:
        # first two digits, period, next digit
        abbr_string = f"{first_digit}{second_digit}.{third_digit}{letter}"
    if number_length % 3 == 1:
        # first digit, period, next two digits
        abbr_string = f"{first_digit}.{second_digit}{third_digit}{letter}"

    return abbr_string
# }}}


def dict_to_rich_table(input_table: list[dict]):
    # turn this list[dict] into a rich.Table
    # rich_table = Table(title="Countries")
    # for i, row in enumerate(table):
    #     if i == 0:
    #         rich_table.add_column("Key", style="bold", header_style="bold")
    #         for key in row.keys():
    #             rich_table.add_column(key, style="bold", header_style="bold")
    #     rich_table.add_row(str(i), *[str(value) for value in row.values()])
    # console.print(rich_table)
    from rich.console import Console
    from rich.table import Table
    console = Console()
    table = Table(title="Countries")
    table.add_column("Key", style="bold", header_style="bold")
    for key in input_table[0].keys():
        table.add_column(key, style="bold", header_style="bold")
    for i, row in enumerate(input_table):
        table.add_row(str(i), *[str(value) for value in row.values()])
    console.print(table)


def main():
    # from rich import inspect
    # inspect(int, methods=True)
    from waivek.data import Countries
    assert isinstance(Countries, list)
    dict_to_rich_table(Countries)
    ic(Countries)
