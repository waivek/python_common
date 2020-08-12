# COPY PASTE THIS
# import sys
# sys.path = [ "C:/users/vivek/Documents/Python/" ] + sys.path

from colorama import init, Fore, Style
init(convert=True)
import sys
import argparse
import os.path
import json
from columnar import columnar

def print_dict(D):
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
        # if len(str(value)) <= 80:
        #     print("%s: %s" % (key, value))
        # else:
        #     short_value = str(value)[0:70] + " ... " + str(value)[-5:]
        #     value_with_note = "%s // %d characters" % (short_value, len(str(value)))
        #     print("%s: %s" % (key, value_with_note))
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
    cache_contents = file_to_string(cache_path)
    if cache_contents == "":
        cache_contents = "{}"
    cache_D = json.loads(cache_contents)
    return cache_D

def update_json_cache(cache_path, new_cache_D):
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


def print_red_line(string):
    print("{red_color_code}{string}{reset_code}".format(red_color_code=Fore.RED, string=string, reset_code=Style.RESET_ALL))
def print_green_line(string):
    print("{green_color_code}{string}{reset_code}".format(green_color_code=Fore.GREEN, string=string, reset_code=Style.RESET_ALL))

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

def read_stdin():
    # sys.stdout.reconfigure(encoding='utf-8')
    input_stream = sys.stdin
    file_contents = input_stream.read()
    return file_contents
def read_pipe_or_file():
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

import re
class Timestamp():
    def __init__(self, tstamp):
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


import dateutil.parser
from datetime import timedelta
from datetime import datetime
from datetime import timezone
import timeago
class Date:
    def __init__(self, dt_str):
        if isinstance(dt_str, datetime):
            dt_str = dt_str.isoformat()
        INDIAN_TIMEZONE  = dateutil.tz.gettz("IST")
        self.dt = dateutil.parser.parse(dt_str).astimezone(INDIAN_TIMEZONE)
        self.string = self.dt.isoformat()
    def __add__(self, seconds_rhs):
        seconds = int(seconds_rhs)
        return Date(self.dt + timedelta(seconds=seconds))
    def __sub__(self, rhs):
        # Date - int      = Date (earlier date)
        # Date - Date     = int  (total seconds)
        # Date - datetime = int  (total seconds)

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
    def timeago(self):
        now = datetime.now(timezone.utc)
        return timeago.format(self.dt, now)

    def __repr__(self):
        timeago_str = self.timeago()
        return "{formatted_datetime} ({timeago_string})".format(
                formatted_datetime=self.dt.strftime("%I:%M %p, %b %d"),
                timeago_string=timeago_str)

