
# if __package__ is None and __name__ == "__main__":
#     from os.path import sep
#     *_, __package__, _ = __file__.split(sep)

from waivek.timer import Timer   # Single Use
timer = Timer()
from waivek.color import Code    # Multi-Use
from waivek.error import handler # Single Use
# from .ic import ic, ib     # Multi-Use, import time: 70ms - 110ms
from waivek.reltools import rel2abs, read, write
from waivek.db import db_init

DATA_PATH = rel2abs("data/countries.json")
DB_PATH = rel2abs("data/download_epochs.db")
def init():
    import os
    os.makedirs(rel2abs("data"), exist_ok=True)
    if not os.path.exists(DATA_PATH):
        write({}, DATA_PATH)
    connection = db_init(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS download_epoch (name TEXT, epoch INTEGER);")
    connection.commit()
    connection.close()

def get_countries():
    init()
    import time
    connection = db_init(DB_PATH)
    cursor = connection.cursor()
    download_epoch = cursor.execute("SELECT epoch FROM download_epoch WHERE name = 'countries'").fetchone()
    current_epoch = int(time.time())
    one_month_in_seconds = 60 * 60 * 24 * 30
    use_cache = download_epoch is not None and current_epoch - download_epoch[0] < one_month_in_seconds
    if __name__ == "__main__":
        print(f"{use_cache = }")
    if use_cache:
        table = read(DATA_PATH)
        return table

    from waivek.get import aget
    import json

    urls = ["https://raw.githubusercontent.com/samayo/country-json/master/src/country-by-population.json",
            "https://raw.githubusercontent.com/samayo/country-json/master/src/country-by-capital-city.json"]
    responses = aget(urls, cache=False)
    dictionaries = [ json.loads(response) for response in responses ]
    dicts_1, dicts_2 = dictionaries
    # dicts_1: [ { "country": ..., "population": ... } ]
    # dicts_2: [ { "country": ..., "city": ... } ]

    # dicts_3: [ { "country": ..., "population": ..., "city": ... } ]
    dicts_3 = []
    for dict_1 in dicts_1:
        for dict_2 in dicts_2:
            if dict_1["country"] == dict_2["country"]:
                dict_3 = dict_1.copy()
                dict_3.update(dict_2)
                dicts_3.append(dict_3)
                break
    # sort on population
    dicts_3.sort(key=lambda dict_3: dict_3["population"], reverse=True)
    top_20 = dicts_3[:20]
    write(top_20, DATA_PATH)
    cursor.execute("INSERT OR REPLACE INTO download_epoch (name, epoch) VALUES ('countries', ?);", (current_epoch,))
    connection.commit()
    return top_20

def main():
    from waivek.ic import ic
    Countries = get_countries()
    ic(Countries)
    from rich import print, inspect
    from waivek.ic import ib
    from datetime import datetime
    # ib(datetime)
    # inspect(datetime

Countries = get_countries()

if __name__ == "__main__":
    with handler():
        main()

