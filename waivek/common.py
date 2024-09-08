# COPY PASTE THIS
# import sys
# sys.path = [ "C:/users/vivek/Documents/Python/" ] + sys.path

# How to Install: 
# 
#   pip install https://github.com/waivek/python_common/archive/master.zip
#    
#    PHP FUNCTIONS:
#       (list)  array_chunk
#       (dict)  array_count_values
#       (table) array_column
#       (dict)  array_extrace
#
# Refactory:
#
#       abbr(number)
#       trunc(string, length)
#       pad_zero(current_value, max_value)
#       pad_space(current_value, max_value)
#       enumerate_count(items)
#       rel2abs(relative_path)
#
from waivek.timer import Timer
from waivek.color import Code
timer = Timer()

import sys
import os.path


def rel2abs(relative_path):
    from waivek.reltools import rel2abs as func
    return func(relative_path)

def print_error_information(error):
    from waivek.error import print_error_information as func
    func(error)

def stub_quiet():
    t = Timer()

# --- START


def create_partitions_2(size, n):
    starts = list(range(0, size, n))
    ends = starts[1:] + [ size ]
    return list(zip(starts, ends))

def create_partitions_old(max_value, partition_value):
    import math
    number_of_partitions = math.ceil(float(max_value) / partition_value)
    starts = [ i * partition_value for i in range(number_of_partitions) ]
    ends = starts[1:] + [max_value]
    return [(start, end) for start, end in zip(starts, ends)]

def create_partitions(max_value, partition_value):
    indices = list(range(0, max_value, partition_value)) + [ max_value ]
    return list(zip(indices, indices[1:]))


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

def smart_pad(current_value, max_value, fillchar='0'):
    number_of_digits = len(str(max_value))
    return str(current_value).rjust(number_of_digits, fillchar)

def enumerate_count(items):
    item_count = len(items)
    count_strings = []
    for i in range(item_count):
        count_str = smart_pad(i+1, item_count)
        count_strings.append(f"[{count_str}/{item_count}]")
    return zip(count_strings, items)

def print_object(obj, hidden=False):
    if not hidden:
        keys = [ key for key in dir(obj) if not key.startswith("__") ]
    else:
        keys = dir(obj)
    D = { key : obj.__getattribute__(key) for key in keys }
    print_dict(D)


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

def make_pretty(json_filepath):
    import json
    with open(json_filepath, "r") as f:
        dictionaries = json.load(f)
    filepath, extension = os.path.splitext(json_filepath)
    pretty_json_filepath = filepath + f"-pretty{extension}"
    with open(pretty_json_filepath, "w") as f:
        json.dump(dictionaries, f, indent=4)

    message = f"{json_filepath} -> {pretty_json_filepath}"
    print(message)

def to_json(obj, filepath):
    import json
    with open(filepath, "w") as fp:
        json.dump(obj, fp, indent=4)

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

def print_dict(D):
    from columnar import columnar
    if type(D) != type({}):
        argument_type = str(type(D))
        print_red_line("Please pass a dictionary. Invalid type {arg_type} with str representation {str_rep}".format(arg_type=argument_type, str_rep=str(D)))
        return
    data = []
    for key, value in D.items():
        trunc_val = truncate(str(value), 80)
        trunc_val = str(value)
        data.append([key, trunc_val])
    headers = [ "key", "value" ]
    table = columnar(data, headers, no_borders=True)
    print(table)
            

def file_to_string(file_path):
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "rb") as f:
        file_contents = f.read().decode("utf-8")
    return file_contents

def read_json_cache(cache_path):
    import json
    cache_contents = file_to_string(cache_path)
    if cache_contents == "":
        cache_contents = "{}"
    cache_D = json.loads(cache_contents)
    return cache_D

def update_json_cache(cache_path, new_cache_D):
    import json
    cache_contents = file_to_string(cache_path)
    if cache_contents == "":
        cache_contents = "{}"
    old_cache_D = json.loads(cache_contents)
    if old_cache_D == new_cache_D:
        return

    new_cache_contents = json.dumps(new_cache_D)
    with open(cache_path, "wb") as f:
        f.write(new_cache_contents.encode("utf-8"))
        print("[WRITE] {filename}".format(filename=f.name))


def make_string_green(string):
    # from .colorama import init, Fore
    # init(convert=True)
    # return "{color_code}{string}{reset_code}".format(color_code=Fore.GREEN, string=string, reset_code=Fore.RESET)
    return Code.GREEN + string
def make_string_red(string):
    # from .colorama import init, Fore
    # init(convert=True)
    # return "{color_code}{string}{reset_code}".format(color_code=Fore.RED, string=string, reset_code=Fore.RESET)
    return Code.RED + string
def print_red_line(string):
    print(make_string_red(string))
def print_green_line(string):
    print(make_string_green(string))

# for copy-pasting into libraries
def truncate_2(s, L):
    # M: middle_part, S: slice_size, s: string, T: trunc_string, R: right_start, L: length
    if len(s) <= L:
        return s
    M = "..."
    S = int((L-len(M))/2)
    R = S + int(L % 2 == 0)
    T = s[0:S]+M+s[-R:]
    return T if len(T) == L else s

def truncate(string, length):
    if len(string) <= length:
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
        print_red_line(f"[common.py:func=truncate] ERROR: Could not return a truncated string. (string={repr(string)}, length={length})")
        return "ERROR"
    return trunc_string

def read_stdin():
    # sys.stdout.reconfigure(encoding='utf-8')
    input_stream = sys.stdin
    file_contents = input_stream.read()
    return file_contents
def read_pipe_or_file():
    import argparse
    stream_is_interactive = sys.stdin.isatty()
    if stream_is_interactive:
        parser = argparse.ArgumentParser(description="Removes attributes from a HTML file")
        parser.add_argument("input_filename")
        args = parser.parse_args()
        with open(args.input_filename, "rb") as f:
            file_contents = f.read().decode("utf-8")
    else:
        file_contents = read_stdin()
    return file_contents

class Timestamp():
    def __init__(self, tstamp):
        import re
        if type(tstamp) == str and re.match(r'^[0-9.]+$', tstamp):
            tstamp = int(tstamp)
        if type(tstamp) == str:
            m = re.match(r'\d?\dhh?\d?\dmm?\d?\ds?', tstamp)
            if m:
                # tstamp is in 01h02m03s format
                tstamp = re.sub(r'[hm]+', ":", tstamp).replace("s", "")
            a, b, c = tstamp.split(":")
            self.hh = int(a)
            self.mm = int(b)
            self.ss = int(float(c))
            self.timestamp = tstamp
            self.seconds = self.hh * 3600 + self.mm * 60 + self.ss
        elif type(tstamp) == float or type(tstamp) == int:
            seconds_placeholder = int(tstamp)
            self.seconds = seconds_placeholder
            self.hh = int(seconds_placeholder / 3600)
            seconds_placeholder = seconds_placeholder % 3600
            self.mm = int(seconds_placeholder / 60)
            seconds_placeholder = seconds_placeholder % 60
            self.ss = seconds_placeholder 
        self.timestamp = "{hours:02}:{minutes:02}:{seconds:02}".format(hours=self.hh, minutes=self.mm, seconds=self.ss)
        self.hh_mm_ss = "{hours:02}h{minutes:02}m{seconds:02}s".format(hours=self.hh, minutes=self.mm, seconds=self.ss)
    def __repr__(self):
        if self.seconds == 1:
            return "00:00:01: 1 second" 
        return "%s: %d seconds" % (self.timestamp, self.seconds)
    def __add__(a, b):
        return Timestamp(a.seconds + b.seconds)
    def __sub__(a, b):
        return Timestamp(abs(a.seconds - b.seconds))
    def days(self):
        d = int(self.hh % 24)
        hh = self.hh / 24
        return "%d days %02d:%02d:%02d" % (d, hh, self.mm, self.ss)


class Date:
    def __init__(self, string_or_datetime_or_epoch):
        import dateutil.parser
        from datetime import datetime
        from datetime import timezone
        from datetime import timedelta
        if isinstance(string_or_datetime_or_epoch, datetime):
            dt_str = string_or_datetime_or_epoch.isoformat()
        elif isinstance(string_or_datetime_or_epoch, int) or isinstance(string_or_datetime_or_epoch, float):
            dt_str = datetime.fromtimestamp(string_or_datetime_or_epoch).isoformat()
        else:
            dt_str = string_or_datetime_or_epoch
        # INDIAN_TIMEZONE  = dateutil.tz.gettz("Asia/Kolkata")
        INDIAN_TIMEZONE = timezone(timedelta(hours=5, minutes=30), 'IST')

        self.dt = dateutil.parser.parse(dt_str).astimezone(INDIAN_TIMEZONE).replace(microsecond=0)
        self.string = self.dt.isoformat()
        self.epoch = int(self.dt.timestamp())

    def timeago(self):
        from datetime import timezone
        import timeago
        from datetime import datetime
        now = datetime.now(timezone.utc)
        return timeago.format(self.dt, now)

    def now():
        from datetime import datetime
        return Date(datetime.now())

    def pretty(self):
        from datetime import timezone
        print_dict({
            "ist": self.string,
            "utc": self.dt.astimezone(timezone.utc).isoformat()[:-6],
            "epoch": self.epoch,
            "timeago": self.timeago()
        })

    # `=`, `+`, `-`, `<`, `>`, str, repr {{{
    def __eq__(self, rhs_date):
        return self.dt == rhs_date.dt
    def __add__(self, seconds_rhs):
        seconds = int(seconds_rhs)
        from datetime import timedelta
        return Date(self.dt + timedelta(seconds=seconds))
    def __sub__(self, rhs):
        # Date - int      = Date (earlier date)
        # Date - Date     = int  (total seconds)
        # Date - datetime = int  (total seconds)

        from datetime import timedelta
        from datetime import datetime
        if type(rhs) == int:
            difference_datetime = self.dt - timedelta(seconds=rhs)
            return Date(difference_datetime)
        elif type(rhs) == Date:
            difference_timedelta = self.dt - rhs.dt
            return difference_timedelta.total_seconds()
        elif type(rhs) == datetime:
            difference_timedelta = self.dt - rhs
            return difference_timedelta.total_seconds()

    def __lt__(self, other):
        return self.dt < other.dt
    def __gt_(self, other):
        return self.dt > other.dt
    def __str__(self):
        timeago_str = self.timeago()
        return "{formatted_datetime} ({timeago_string})".format(
                formatted_datetime=self.dt.strftime("%I:%M %p, %b %d"),
                timeago_string=timeago_str)
    def __repr__(self):
        repr_string = repr(self.string)
        return f"Date({repr_string})"
    def __format__(self, string):
        return self.dt.strftime(string)
    # }}}

if __name__ == "__main__":
    from waivek.ic import ic
    error_table = [{'slug': 'ThankfulDeadMinkJonCarnage-A1wuckc0t442Zdzx', 'views': 384, 'user_id': '160504245', 'title': 'lacari playing gwen', 'thumbnail_url': 'https://clips-media-assets2.twitch.tv/AT-cm%7CtyYhdQNcLnJHNLeONmXc8Q-preview-480x272.jpg'}]
    ic(error_table)
    pass

# run.vim: term python waivek/test_error2.py
