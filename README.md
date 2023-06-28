Code - Print colored text

```
from waivek import Code
print(Code.RED + "Hello, World!")
```

common

```
from waivek import Date, Timestamp
dt = Date("2020-01-01"
timestamp = Timestamp(3600)
```

```
>>> Date(1672511400) == Date('2023-01-01')
True

>>> date = Date(1672511400)
>>> date
12:00 AM, Jan 01 (5 months ago)

>>> date.epoch
1672511400

>>> date.string
2023-01-01T00:00:00+05:30

>>> date.timeago()
5 months ago

>>> str(date)
12:00 AM, Jan 01 (5 months ago)

>>> date.dt
2023-01-01 00:00:00+05:30
```


```
from waivek import create_partitions, smart_pad, enumerate_count
```

db

```
from waivek import db_init, insert_dictionaries
cursor, connection = db_init(db_path)
insert_dictionaries(cursor, table_name, dictionaries)
```

error

```
from waivek import handler
with handler():
    main()
```

get

```
from waivek import aget
aget(urls)
```

ic

```
from waivek import ic, ib
ic({"key": "value"})
ib(str)
```

print\_utils - Print and manipulate text.

```
from waivek import head, truncate, abbreviate
```

reltools - Do path manipulation relative to 

```
from waivek import rel2abs, read, write
```

timer - Measure execution time of code snippets

```
from waivek import Timer
```
