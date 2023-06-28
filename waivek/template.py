from waivek import Timer   # Single Use
timer = Timer()
from waivek import Code    # Multi-Use
from waivek import handler # Single Use
from waivek import ic, ib     # Multi-Use, import time: 70ms - 110ms
Code; ic; ib; handler

def main():
    pass

if __name__ == "__main__":
    with handler():
        main()
