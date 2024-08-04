from waivek import Timer   # Single Use
timer = Timer()
from waivek import Code    # Multi-Use
from waivek import handler # Single Use
from waivek import ic, ib     # Multi-Use, import time: 70ms - 110ms
from waivek import rel2abs

from waivek.loglib import log, add_file_handler

def message():
    x = 1
    y = func(x)
    log("Goodbye, World!")

