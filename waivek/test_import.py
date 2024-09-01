import os
from waivek.nest.nested import greet_nested, new_addition
from waivek.test_relimport import greet_relative

def greet(): print(f"[{os.path.basename(__file__)}] Hello, World!")


if __name__ == "__main__":
    print(f"[{__file__}] __name__ = {__name__}")
    greet()
    greet_relative()
    greet_nested()
    new_addition()
