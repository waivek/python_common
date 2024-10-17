# [NOTE:4/6] Without this, we can’t compile type hints like loguru.Record; see: https://loguru.readthedocs.io/en/stable/api/type_hints.html
from __future__ import annotations
from waivek.timer import Timer
timer = Timer()

from datetime import datetime, timedelta
import sys
import os.path
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import loguru

logger: loguru.Logger
STDOUT_HANDLER_ID: int

def custom_message_formatter(record: loguru.Record):
    # [NOTE:6/6] <level> always adds an ANSI reset code at the end of the message, even if we specify color="" as we have don above
    if record["level"].name == "INFO":
        return f"{record['message']}" + "\n{exception}"
    return f"<level>{record['message']}</level>" + "\n{exception}"

def configure_global_logger():
    global logger
    if "logger" in globals():
        return
    global STDOUT_HANDLER_ID
    import loguru
    logger = loguru.logger
    logger.remove()

    # [NOTE:5/6] We want to use the default `white` of the terminal, which is different from <white> or <light-white> in loguru
    logger.level("INFO", color="")

    # [NOTE:1/6] Note that it’s not possible to chain opt() calls, the last one takes precedence over the others as it will “reset” the options to their default values. (from the docs https://loguru.readthedocs.io/en/stable/api/logger.html#loguru._logger.Logger.opt)
    logger = logger.opt(colors=True, depth=1) # make sure to put all the `opt` in a single call, don’t separate them

    # loguru_format_stdout = "<level>{message}</level>"
    # STDOUT_HANDLER_ID = logger.add(sys.stdout, colorize=True, format=loguru_format_stdout)
    STDOUT_HANDLER_ID = logger.add(sys.stdout, colorize=True, format=custom_message_formatter)

def set_verbose_stdout():
    # change the format of the stdout handler
    global STDOUT_HANDLER_ID
    global logger
    configure_global_logger()
    logger.remove(STDOUT_HANDLER_ID)
    STDOUT_HANDLER_ID = logger.add(sys.stdout, colorize=True, format=custom_file_formatter)

def custom_file_formatter(record: loguru.Record):
    # [NOTE:2/6] to see why we do \n{exception} see: https://loguru.readthedocs.io/en/stable/api/logger.html#message

    # loguru_format_file = "<green>{time:YYYY-MM-DDTHH:mm:ssZ}</green> <cyan>{file}:{line}</cyan> <level>{level: <8}</level> - <level>{message}</level>"
    # [NOTE:3/6] we aren’t using the above as we want to align the file name and line number in our log files.
    record_file: loguru.RecordFile = record["file"]
    file_tag = f"{record_file.name}:{record['line']}"

    return f"{record['time'].strftime('%Y-%m-%dT%H:%M:%S%z')} {file_tag:>20} {record['level']:<7} - {record['message']}" + "\n{exception}"

def add_file_handler(file_path):
    if not os.path.isabs(file_path):
        raise ValueError(f"file_path must be an absolute path. {file_path = }")
    if not os.path.exists(os.path.dirname(file_path)):
        raise ValueError(f"Directory does not exist. {os.path.dirname(file_path) }")

    global logger
    configure_global_logger()
    # logger.add(file_path, colorize=False, format=loguru_format_file)
    logger.add(file_path, colorize=False, format=custom_file_formatter)

def log(message, level="INFO"):
    global logger
    configure_global_logger()
    # logger.opt(depth=1).log(level, message)

    logger.log(level, message)

def print_loguru_defaults():
    from loguru._defaults import LOGURU_FORMAT
    from loguru._logger import Core
    from waivek.ic import ic
    print(LOGURU_FORMAT)
    levels = Core().levels
    ic(levels)

def will_always_error_large_json_object():
    import json
    # intentional error
    json.loads(1) # type: ignore
    json_string = """
    {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3",
        "key4": "value4",
        "key5": "value5",
        "key6": "value6",
        "key7": "value7"
    }"""
    json_object = json.loads(json_string)
    error_key = json_object["key8"]["key9"]

def will_always_error():
    x = 1
    y = 0
    z = x / y
    return z
    
def experiments():
    from waivek.reltools import rel2abs
    from waivek.ic import ic
    log_path = rel2abs("data/experiments.log")
    with open(log_path, "w") as f:
        f.write("")
    add_file_handler(log_path)
    log("Hello, World!", "ERROR")
    log("Hello, World!", "WARNING")
    log("Hello, <blue>World!</blue>")
    log("<fg black><bg red><bold> OSError </bold></bg red></fg black>")
    message = "Custom Message"
    log(f"{message = }")
    try:
        # will_always_error_large_json_object()
        pass
    except Exception as e:
        logger.opt(exception=True).error("An error occurred.")

    print("\nLog file contents: " + log_path + "\n")
    with open(log_path, "r") as f:
        contents = f.read()
        print(contents)

def test_1():
    # redirect to file
    log("Hello, World!")
    log("Something went wrong", "ERROR")

def foo():
    # print_loguru_defaults()
    # experiments()
    test_1()

if __name__ == "__main__":
    foo()

# run.vim: vert term python waivek/__init__.py

