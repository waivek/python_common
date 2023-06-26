
color

```
from color import Code
print(Code.RED + "Hello, World!")
```

common

```
from common import Date, Timestamp
dt = Date("2020-01-01"
timestamp = Timestamp(3600)
```

```
from common import create_partitions, smart_pad, enumerate_count
```

db

```
from db import db_init, insert_dictionaries
cursor, connection = db_init(db_path)
insert_dictionaries(cursor, table_name, dictionaries)
```

error

```
from error import handler
with handler():
    main()
```

get

```
from get import aget
aget(urls)
```

ic

```
from ic import ic, ib
ic({"key": "value"})
ib(str)
```

print\_utils

```
from print_utils import head, truncate, abbreviate
```

reltools

```
from reltools import rel2abs, read, write
```

timer

```
from timer import Timer
```
