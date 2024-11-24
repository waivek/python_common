from box import Timer   # Single Use
timer = Timer()
from box import Code    # Multi-Use
from box import handler # Single Use
from box import ic, ib     # Multi-Use, import time: 70ms - 110ms
from box import rel2abs

from box.log import log, add_file_handler, set_verbose_stdout


def main():
    log_path = rel2abs('data/sink.log')
    with open(log_path, 'w') as f:
        f.write("")
    add_file_handler(log_path)
    from examplelog2 import message
    log("Hello World!")
    message()
    with open(log_path, 'r') as f:
        print(f.read())

    
if __name__ == "__main__":
    with handler():
        main()
