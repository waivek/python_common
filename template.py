import sys; sys.path = [ "C:/users/vivek/Documents/Python/" ] + sys.path
from timer import Timer   # Single Use
timer = Timer()
from color import Code    # Multi-Use
from error import handler # Single Use
from ic import ic, ib     # Multi-Use, import time: 70ms - 110ms

def unused_silencer():
    Code, ic, ib

def main():
    pass

if __name__ == "__main__":
    with handler():
        main()
