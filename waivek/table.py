
import os
import sys
from waivek.truncate import get_display_length, truncate

from color import Code

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
    from waivek.db import sqlite3
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
