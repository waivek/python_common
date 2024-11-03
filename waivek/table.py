import os
import sys
from waivek.truncate import get_display_length, truncate
from waivek.common import enumerate_count

from color import Code
import rich

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

def get_max_width_and_height():
    in_terminal = sys.stdout.isatty()
    if in_terminal:
        return os.get_terminal_size()
    else:
        return (200, 200)
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

def pad_lines(lines: list[str], line_count=1):
    """
    Adjusts the input list of lines to match the specified line_count.

    If the number of input lines is less than or equal to line_count,
    the function pads the list with blank lines to reach the desired height.
    If the number of input lines exceeds line_count, it truncates the list
    from both ends and inserts an ellipsis ("...") in the middle.
    """
    list_height = len(lines)
    if list_height <= line_count:
        # vjust
        blank_line_count = line_count - list_height
        max_length = max(len(line) for line in lines)
        blank_lines = [ " " * max_length for _ in range(blank_line_count) ]
        return lines + blank_lines
    else:
        # vtruncate
        top_end = int(line_count/2)
        bot_start = list_height - int(line_count/2) + 1
        truncated_lines = lines[0:top_end] + [ "..." ] + lines[bot_start:]
        # if len(slice_L) != line_count: error {{{
        if len(truncated_lines) != line_count:
            print(Code.RED +  "(error) v_pad(list_string, line_count)")
            print(Code.RED + f"....... len(slice_L): {len(truncated_lines)}")
            print(Code.RED + f"....... line_count  : {line_count}")
            raise Exception("len(slice_L) != line_count")
        # }}}
        return truncated_lines

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
                v_pad_cells = [ pad_lines(cell.split("\n"), largest_height) for cell in cells ]
                return_lines = []
                for i in range(largest_height):
                    parts = [ cell[i] for cell in v_pad_cells ]
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

def to_table(rows):
    T = Table()
    for row in rows:
        T.row(row)
    return T

def test_table():
    from waivek.ic import ic
    merged_test_cases = [
        ("is_tuple_table", [ ("a", "b", "c"), ("d", "e", "f"), ("g", "h", "i") ]),
        ("is_tuple_table", [(1, 2), (3, 4)]),   # List of tuples
        ("is_tuple_table", [[1, 2], [3, 4]]),   # List of lists

        ("is_single_dict_table", {"d": "e", "a": "b"}),  # Dictionary
        ("is_single_dict_table", [{"key": "value"}]), # List of dictionaries

        ("is_multi_dict_table", [{"key1": "value1"}, {"key1": "value2"}]),  # Same keys

    ]

    ic({"d": "e", "a": "b"})
    name, table = merged_test_cases[0]
    for count_str, (name, table) in enumerate_count(merged_test_cases):
        try:
            T = to_table(table)
            print(T)
        except Exception as error:
            rich.print(f"{count_str} [black on red] FAIL [/] {repr(table)}")
            print(error.__class__.__name__)
            print("===")
        rich.print(f"{count_str} [black on green] PASS [/]")
        print("===")

if __name__ == "__main__":
    test_table()
