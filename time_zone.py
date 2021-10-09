
from columnar import columnar
import sys
sys.path = [ "C:/users/vivek/Documents/Python/" ] + sys.path
from common import print_red_line
from datetime import datetime
from datetime import timedelta
import dateutil
import re
import timeago

def day_name(dt):
    return dt.strftime("%A")


string = "tuesday 12pm pst"
string = " ".join(sys.argv[1:])
# string_2 = "12pm pst tuesday"

string = string.lower()
input_day = re.search("(mon|tues|wednes|thurs|fri|satur|sun)day", string).group(0)
timezone = re.search(r'\bpst|est|cst\b', string).group(0)
time_m = re.search("(?P<hours>\d?\d):?(?P<minutes>\d\d)? ?(?P<meridiem>pm|am)", string)
input_hours = time_m.group("hours")
input_minutes = time_m.group("minutes") if time_m.group("minutes") else "00"
input_meridiem = time_m.group("meridiem")
input_time = "{hh}:{mm} {merdiem}".format(hh=input_hours, mm=input_minutes, merdiem=input_meridiem)
strp = datetime.strptime(input_time, "%I:%M %p")
time_string = datetime.strftime(strp, "%H:%M") # 24 hour clock
input_hours, input_minutes = time_string.split(":")
input_hours = int(input_hours)
input_minutes = int(input_minutes)


expand_timezone_D  = { 
    "PST": "Pacific Standard Time", 
    "EST": "Eastern Standard Time", 
    "CST" : "Central Standard Time",
    "IST" : "India Standard Time"
}
full_timezone = expand_timezone_D[timezone.upper()]

timezone_tz  = dateutil.tz.gettz(full_timezone)
if not timezone_tz:
    print_red_line("Invalid timezone: {timezone}".format(timezone=timezone))
    sys.exit(1)
now = datetime.now().astimezone(timezone_tz)
target = now
while day_name(target).lower() != input_day:
    target = target + timedelta(days=1)

target = target.replace(hour=input_hours, minute=input_minutes, second=0)
if target < now:
    target = target + timedelta(days=7)

pst_string = target.strftime("%I:%M %p, %b %d")
target_ist = target.astimezone(dateutil.tz.gettz("India Standard Time"))
ist_string = target_ist.strftime("%I:%M %p, %b %d")

timeago_string = timeago.format(target_ist, now)
ist_string = "{a} ({b})".format(a=ist_string, b=timeago_string)


headers = [ timezone.upper(), "IST" ]
data = [ [ pst_string, ist_string ] ]
table = columnar(data, headers, no_borders=True)

padding = " " * 4
print("{input_timezone}{padding}IST".format(input_timezone=timezone.upper().ljust(len(pst_string)), padding=padding))
print("{pst_string}{padding}{ist_string}".format(pst_string=pst_string, padding=padding, ist_string=ist_string))

