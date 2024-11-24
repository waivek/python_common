

from abc import abstractmethod
from datetime import datetime
from zoneinfo import ZoneInfo

from box.ic import ic

from box.date import get_now, DateTimeTZ

now = DateTimeTZ.from_datetime(get_now("Asia/Kolkata"))
from box.log import log
log("Hello, World!")
