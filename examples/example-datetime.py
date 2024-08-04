

from abc import abstractmethod
from datetime import datetime
from zoneinfo import ZoneInfo

from waivek.ic import ic

from waivek.date import get_now, DateTimeTZ

now = DateTimeTZ.from_datetime(get_now("Asia/Kolkata"))
from waivek.log import log
log("Hello, World!")
