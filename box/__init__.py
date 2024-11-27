from box.timer import Timer
timer = Timer(precision=3)
from typing import TYPE_CHECKING # used in a lot of places, so import it here

from box.color import Code
from box.common import create_partitions, smart_pad, enumerate_count
from box.common import Timestamp, Date
# timer.start("import db_init, insert_dictionaries")
from box.db import db_init, insert_dictionaries # slow: 0.03s
# timer.print("import db_init, insert_dictionaries")
from box.dbutils import Connection              # slow: 0.02s
from box.error2 import handler # still takes 0.02s, improved with TYPE_CHECKING
from box.get import aget
from box.ic import ic, ib
from box.print_utils import head, truncate, abbreviate
from box.reltools import rel2abs, read, write, readlines, writelines
# timer.start("import pack, unpack")
from box.introspection import pack, unpack
# timer.print("import pack, unpack")
from box.log import log, add_file_handler, set_verbose_stdout
from box.bat import bat
from box.markup import markup

from box.jsonfile import usable

from box.db_api_base import get_pagination, get_clusters_sqlalchemy

# from box.data import Countries
