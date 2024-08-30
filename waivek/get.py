
# Asynchronous Getting
# 0. Get JSON / READ / TEXT / RESPONSE (sync)
# 1. Toggleable Caching - render_chat.py:get_images_cached(urls)
# 2. Configurable Connection Limit - render_chat.py:get_json_batch(urls, limit=100)
# 3. Toggleable AsyncInfo - Log status url reason counts
# 4. Handle status codes 404 and non-200
# 5. Configureable url2header Function
# 6. POST with payload

from waivek.timer import Timer   # Single Use
timer = Timer()

from waivek.db import db_init
from waivek.color import Code

# import aiohttp
# import asyncio
import json

aiohttp = None
asyncio = None
connection = None

class Config:
    cache = True
    log = True
    url2header = lambda url: {}
    url2cookie = lambda url: {}
    limit = 100

class Response:
    def __init__(self, response, obj):
        self.url = str(response.url)
        self.status = response.status
        self.ok = response.ok
        self.reason = response.reason
        self.headers = {row[0]: row[1] for row in response.headers.items()}
        self.obj = obj
        self.total_bytes = response.content.total_bytes
    def __repr__(self):
        return f"Response <{self.status}>"


class AsyncInfo:
    def __init__(self, lock):
        self.lock = lock
        self.results = []
        self.total = 0
        self.count_pass = 0
        self.count_fail = 0
        self.code_counter = {}

    def add(self, response):
        url = response.url
        reason = response.reason
        status = response.status

        self.results.append({ 'url': url, 'status': status, 'reason': reason })
        self.total = self.total + 1 
        if status == 200:
            self.count_pass = self.count_pass + 1
        else:
            self.count_fail = self.count_fail + 1
        self.code_counter[status] = self.code_counter.get(status, 0) + 1

    def print(self):
        code_strings = []
        for code in sorted(self.code_counter.keys()):
            count = self.code_counter[code]
            color = Code.GREEN if code < 400 else Code.RED
            code_strings.append(color + f"{code}: {count}")
        code_string = "{ " + ", ".join(code_strings) + " }"
        print(f"Total: {self.total} Pass: {self.count_pass} Fail: {self.count_fail} Codes: {code_string}", end="\r")

def configure_asyncio():
    global asyncio
    global aiohttp
    import asyncio
    import aiohttp

    if Config.log:
        global async_info
        async_info = AsyncInfo(asyncio.Lock())

    import platform
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def is_binary(content_type):
    mime_type, subtype = content_type.split("/")

    if mime_type == "text":
        return False
    if mime_type != "application":
        return True
    return subtype not in ["json", "ld+json", "x-httpd-php", "x-sh", "x-csh", "xhtml+xml", "xml"]

# read text json content_type
async def async_response_to_sync_response(response):
    # https://stackoverflow.com/questions/57565577/how-to-return-aiohttp-like-python-requests
    # https://docs.aiohttp.org/en/stable/client_reference.html#response-object
    if response.content_type == 'application/json':
        obj = await response.json()
    elif is_binary(response.content_type):
        obj = await response.read()
    else:
        obj = await response.text()
    return Response(response, obj)

async def log_response(response):
    if Config.log:
        async with async_info.lock:
            async_info.add(response)
            async_info.print()

async def get_async(url, session):
    headers = Config.url2header(url)
    cookies = Config.url2cookie(url)
    # breakpoint()
    response = await session.get(url, headers=headers, cookies=cookies)
    async with response:
        sync_response = await async_response_to_sync_response(response)
    await log_response(response)

    return sync_response

async def batch_get_async(urls):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=Config.limit), trust_env=True) as session:
        cors = [ get_async(url, session) for url in urls ]
        responses = await asyncio.gather(*cors)
    if Config.log and len(urls) > 0:
        print()
    return responses

def get_nocache(urls):
    configure_asyncio()
    # [ obj ]
    responses = asyncio.run(batch_get_async(urls))
    return responses

# -- START: CACHE --
def to_temp_table(cursor, items, table_string):
    table_name = table_string.split(" ")[0]
    cursor.execute(f"CREATE TEMP TABLE {table_string};")
    cursor.executemany(f"INSERT INTO {table_name} VALUES (?);", [ (item,) for item in items ])

def get_cached_urls(urls):
    cursor = connection.cursor()
    to_temp_table(cursor, urls, "urls (url TEXT UNIQUE)")
    uncached_urls = [ url for url, in cursor.execute("SELECT url FROM urls WHERE url IN (SELECT url FROM cache);").fetchall() ]
    cursor.execute("DROP TABLE urls;")
    return uncached_urls


def get_uncached_urls(urls):
    cursor = connection.cursor()
    to_temp_table(cursor, urls, "urls (url TEXT UNIQUE)")
    uncached_urls = [ url for url, in cursor.execute("SELECT url FROM urls WHERE url NOT IN (SELECT url FROM cache);").fetchall() ]
    cursor.execute("DROP TABLE urls;")
    return uncached_urls

def object_to_type(obj):
    if type(obj) is str:
        return 'text'
    elif type(obj) is bytes:
        return 'binary'
    else:
        return 'json'

def cache(urls, objects):
    cursor = connection.cursor()
    tuples = []
    for url, obj in zip(urls, objects):
        obj_type = object_to_type(obj)
        obj = json.dumps(obj) if obj_type == 'json' else obj
        T = (url, obj_type, obj)
        tuples.append(T)

    cursor.executemany("INSERT INTO cache (url, type, response) VALUES (?, ?, ?);", tuples)
    connection.commit()

def cache_get(urls):
    cursor = connection.cursor()
    to_temp_table(cursor, urls, "urls (url TEXT UNIQUE)")
    url_to_object_D = { url: response for url, response in cursor.execute("SELECT url, response FROM cache WHERE url IN (SELECT url FROM urls);") }
    url_to_type_D = { url: type for url, type in cursor.execute("SELECT url, type FROM cache WHERE url IN (SELECT url FROM urls);") }
    objects = []
    for url in urls:
        object_type = url_to_type_D[url]
        obj = url_to_object_D[url]
        if object_type == 'json':
            obj = json.loads(obj)
        objects.append(obj)
    cursor.execute("DROP TABLE urls;")
    return objects

def get_yescache(urls):
    # -> [ obj | Response ]
    cursor = connection.cursor()
    if DEBUG:
        cursor.execute("DROP TABLE IF EXISTS cache;")
    cursor.execute("CREATE TABLE IF NOT EXISTS cache (url TEXT UNIQUE, type TEXT, response);")

    unique_urls = list(set(urls))
    uncached_urls = get_uncached_urls(unique_urls)
    responses = get_nocache(uncached_urls) if len(uncached_urls) > 0 else []
    pass_objects = [ response.obj for response in responses if response.ok ]
    cache(uncached_urls, pass_objects)

    cached_urls = get_cached_urls(unique_urls)
    cached_objects = cache_get(cached_urls)
    D1 = { url: obj for url, obj in zip(cached_urls, cached_objects) }
    D2 = { url: response.obj if response.ok else response for url, response in zip(uncached_urls, responses) }
    url_to_object_D = D1 | D2 # Dictionary Union
    objects = [ url_to_object_D[url] for url in urls ]
    return objects

# -- END: CACHE --

def aget(urls, cache=True, log=True, limit=100, url2header=lambda url: {}, url2cookie=lambda url: {}):
    # START: Configuration

    global DEBUG
    global Config
    DEBUG = False
    Config.cache = cache
    Config.log = log
    Config.url2header = url2header
    Config.url2cookie = url2cookie
    Config.limit = limit
    if Config.cache:
        global connection
        connection = db_init("aget_cache/cache.db")
    # END: Configuration
    if DEBUG:
        print(Code.RED + "Debug: True")
    if cache:
        objects = get_yescache(urls)
        return objects
    else:
        responses = get_nocache(urls)
        objects = [ response.obj for response in responses ]
        return objects

def run_async_get():
    json_url  = "https://api.betterttv.net/3/cached/emotes/global"
    image_url = "https://cdn.betterttv.net/emote/56e9f494fff3cc5c35e5287e/3x"
    html_url  = "https://example.com/"
    text_url = "https://www.w3.org/TR/PNG/iso_8859-1.txt"
    dupe_url = "https://www.google.com"
    not_found_url = "https://cdn.betterttv.net/emote/404/3x"

    urls = [ json_url, image_url, html_url, text_url, not_found_url, dupe_url, dupe_url ]
    objects = aget(urls, cache=True, log=True)
    ic(objects)
    return objects

if __name__ == "__main__":
    from waivek.ic import ic
    from waivek.error import handler
    with handler():
        run_async_get()
