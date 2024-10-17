from waivek.timer import Timer
timer = Timer(precision=3)
from typing import TYPE_CHECKING # used in a lot of places, so import it here

from waivek.color import Code
from waivek.common import create_partitions, smart_pad, enumerate_count
from waivek.common import Timestamp, Date
# timer.start("import db_init, insert_dictionaries")
from waivek.db import db_init, insert_dictionaries # slow: 0.03s
# timer.print("import db_init, insert_dictionaries")
from waivek.dbutils import Connection              # slow: 0.02s
from waivek.error2 import handler # still takes 0.02s, improved with TYPE_CHECKING
from waivek.get import aget
from waivek.ic import ic, ib
from waivek.print_utils import head, truncate, abbreviate
from waivek.reltools import rel2abs, read, write, readlines, writelines
# timer.start("import pack, unpack")
from waivek.introspection import pack, unpack
# timer.print("import pack, unpack")
from waivek.log import log, add_file_handler, set_verbose_stdout

# from waivek.data import Countries
