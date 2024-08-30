from waivek.timer import Timer
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from waivek.ic import ic
from waivek.color import Code
# from .error import handler
timer = Timer()
import rich
console = rich.get_console()

# PEP 696, disallowing naive datetime objects via type annotations
#
#     [1] https://github.com/python/mypy/issues/10067 - I want to be able to declare "naive datetime" or "aware datetime" as types
#     [2] https://discuss.python.org/t/pep-696-type-defaults-for-typevarlikes/22569

# considerations:
#     
#     [1] datetime.now() is not timezone aware
#     [2] str(datetime) is not ISO 8601 compliant, e.g. `2021-08-31 12:34:56` instead of `2021-08-31T12:34:56`
#     [3] datetime.now(...) has microsecond precision, which is verbose for log files

# BLACKLIST: datetime.now(), str(datetime)

# convert : dt.astimezone(ZoneInfo("Asia/Kolkata"))
# epoch   : int(dt.timestamp())
# string  : dt.isoformat()
# is_naive: dt.tzinfo is None

# timezones:
#
#   timezone.utc
#   ZoneInfo("Asia/Kolkata")
#   ZoneInfo("UTC")
#
# to get the local timezone in a cross-platform way, you can use the tzlocal module

def print_datetime_flaws():
    ic(datetime.now())
    print("... now() is not timezone-aware\n")
    ic(str(datetime.now()))
    print("... str() missing 'T' and timezone or 'Z\n'")
    ic(datetime.now().isoformat())
    print("... isoformat() is verbose, includes microseconds, and missing timezone\n")
    ic(datetime.now(ZoneInfo("Asia/Kolkata")))
    print("... missing 'T'\n")
    ic(datetime.now(ZoneInfo("UTC")).isoformat())
    ic(datetime.now(ZoneInfo("Asia/Kolkata")).isoformat())
    print("... valid\n")

    print(".fromisoformat():")
    ic(datetime.fromisoformat(str(datetime.now())))
    ic(datetime.fromisoformat(str(datetime.now().isoformat())))
    ic(datetime.fromisoformat("2024-08-18 16:54:26.331658+00:00"))

    print("datetime.fromisoformat(2024-08-18 16:54:26.331658Z)" + (Code.LIGHTRED_EX + " ERROR"))


    


def get_now(zone: str): # for IST, use "Asia/Kolkata"
    return datetime.now(ZoneInfo(zone)).replace(microsecond=0)

def foo():
    dt = DateTimeTZ.now(ZoneInfo("Asia/Kolkata"))
    ic(dt.astimezone(ZoneInfo("UTC")))
    ic(int(dt.timestamp()))
    ic(dt.isoformat())

    epoch = 1722394690
    epoch.bit_count

    x = 1
    y = { "zero": 0 }
    print(x/y["zero"])

class DateTimeTZ(datetime):
    """
    A subclass of datetime.datetime that requires all instances to be timezone-aware.
    """
    def __new__(cls, *args, **kwargs):
        # Create the datetime instance
        dt = super().__new__(cls, *args, **kwargs)
        # Check if tzinfo is None or not
        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            raise ValueError("Datetime object must be timezone-aware")
        return dt

    @classmethod
    def now(cls, tz): # pyright: ignore[reportIncompatibleMethodOverride]
        return super().now(tz=tz)

    @classmethod
    def from_datetime(cls, dt: datetime):
        return cls(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond, dt.tzinfo)

if __name__ == "__main__":
    try:
        # foo()
        print_datetime_flaws()
    except Exception as e:
        # handler(e)
        console.print_exception(show_locals=True, extra_lines=0)


