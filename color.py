#
# SEARCH     : print_\(\w\+\)_line(\(.*\))
# SUBSTITUTE : s/print_\(\w\+\)_line(\(.*\))/print(Code.\U\1 + \2)
#
# Doesn’t work for nested function calls example: 
#
#   offsets = [ make_string_green(offset) if offset == None else str(offset) for offset in offsets ]
#
# SEARCH     : make_string_\(\w\+\)(\(.*\))
# SUBSTITUTE : s/make_string_\(\w\+\)(\(.*\))/Code.\U\1\E+\2
#

import platform

class Maker:
    RESET = '\x1b[39m'
    def __init__(self, code):
        self.COLOR = code
    def __add__(self, item):
        str_item = str(item)
        color_str_item = self.COLOR + str_item + self.RESET
        return color_str_item

class Code:
    BLACK           = Maker('\x1b[30m')
    RED             = Maker('\x1b[31m')
    GREEN           = Maker('\x1b[32m')
    YELLOW          = Maker('\x1b[33m')
    BLUE            = Maker('\x1b[34m')
    MAGENTA         = Maker('\x1b[35m')
    CYAN            = Maker('\x1b[36m')
    WHITE           = Maker('\x1b[37m')
    LIGHTBLACK_EX   = Maker('\x1b[90m')
    LIGHTRED_EX     = Maker('\x1b[91m')
    LIGHTGREEN_EX   = Maker('\x1b[92m')
    LIGHTYELLOW_EX  = Maker('\x1b[93m')
    LIGHTBLUE_EX    = Maker('\x1b[94m')
    LIGHTMAGENTA_EX = Maker('\x1b[95m')
    LIGHTCYAN_EX    = Maker('\x1b[96m')
    LIGHTWHITE_EX   = Maker('\x1b[97m')

def print_samples():
    value = [1, 2,3, 4]

    print()
    print(f"{'RED':16} This is the way {Code.RED + value}, I hope you understand")
    print(f"{'LIGHTRED_EX':16} This is the way {Code.LIGHTRED_EX + value}, I hope you understand")
    print()

    print(f"{'GREEN':16} This is the way {Code.GREEN + value}, I hope you understand")
    print(f"{'LIGHTGREEN_EX':16} This is the way {Code.LIGHTGREEN_EX + value}, I hope you understand")
    print()

    print(f"{'YELLOW':16} This is the way {Code.YELLOW + value}, I hope you understand")
    print(f"{'LIGHTYELLOW_EX':16} This is the way {Code.LIGHTYELLOW_EX + value}, I hope you understand")
    print()

    print(f"{'BLUE':16} This is the way {Code.BLUE + value}, I hope you understand")
    print(f"{'LIGHTBLUE_EX':16} This is the way {Code.LIGHTBLUE_EX + value}, I hope you understand")
    print()

    print(f"{'BLACK':16} This is the way {Code.BLACK + value}, I hope you understand")
    print(f"{'LIGHTBLACK_EX':16} This is the way {Code.LIGHTBLACK_EX + value}, I hope you understand")
    print()

    print(f"{'MAGENTA':16} This is the way {Code.MAGENTA + value}, I hope you understand")
    print(f"{'LIGHTMAGENTA_EX':16} This is the way {Code.LIGHTMAGENTA_EX + value}, I hope you understand")
    print()

    print(f"{'CYAN':16} This is the way {Code.CYAN + value}, I hope you understand")
    print(f"{'LIGHTCYAN_EX':16} This is the way {Code.LIGHTCYAN_EX + value}, I hope you understand")
    print()

    print(f"{'LIGHTWHITE_EX':16} This is the way {Code.LIGHTWHITE_EX + value}, I hope you understand")
    print(f"{'WHITE':16} This is the way {Code.WHITE + value}, I hope you understand")
    print()

# LIGHTRED_EX
# LIGHTBLUE_EX | CYAN | LIGHTCYAN_EX
# GREEN
# YELLOW 
# MAGENTA
if __name__ == "__main__":
    if platform.system() == "Windows":

        timer.start("import os, psutil")
        import os, psutil  # Get the parent process name. 
        timer.print("import os, psutil")
        pprocName = psutil.Process(os.getppid()).name()
        print(pprocName)
        # from timer import Timer
        # timer = Timer()
        # timer.start("import init")
        # from colorama import init
        # timer.print("import init")
        # timer.start("init")
        # init(convert=True)
        # timer.print("init")
    print_samples()
