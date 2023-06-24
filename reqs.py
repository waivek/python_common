import sys; sys.path = [ "C:/users/vivek/Documents/Python/" ] + sys.path
from timer import Timer   # Single Use
timer = Timer()
from color import Code    # Multi-Use
from error import handler # Single Use
from ic import ic, ib     # Multi-Use, import time: 70ms - 110ms
Code; ic; ib; handler
from reltools import here

def main():
    from glob import glob
    import os.path
    current_dir = here()
    paths = glob(os.path.join(current_dir, "**/*.py"), recursive=True)
    relpaths = [ path.replace(current_dir, "") for path in paths ]
    ic(relpaths)




if __name__ == "__main__":
    with handler():
        main()

