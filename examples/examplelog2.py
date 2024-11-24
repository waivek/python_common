from box import Timer   # Single Use
timer = Timer()
from box import Code    # Multi-Use
from box import handler # Single Use
from box import ic, ib     # Multi-Use, import time: 70ms - 110ms
from box import rel2abs

from box.log import log, add_file_handler

def message():
    log("Goodbye, World!")

