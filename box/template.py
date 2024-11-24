from box import Timer   # Single Use
timer = Timer()
from box import Code    # Multi-Use
from box import handler # Single Use
from box import ic, ib     # Multi-Use, import time: 70ms - 110ms
Code; ic; ib; handler

def main():
    pass

if __name__ == "__main__":
    with handler():
        main()
