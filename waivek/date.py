from .timer import Timer
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from .ic import ic
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

def get_now(zone: str): # for IST, use "Asia/Kolkata"
    return datetime.now(ZoneInfo(zone)).replace(microsecond=0)

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
        pass
    except Exception as e:
        # handler(e)
        console.print_exception(show_locals=True, extra_lines=0)

