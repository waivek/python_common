# Good Colors:
#
#     LIGHTRED_EX
#     CYAN | LIGHTCYAN_EX
#     LIGHTBLUE_EX 
#     LIGHTGREEN_EX
#     YELLOW 
#     MAGENTA

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

from waivek.timer import Timer
timer = Timer()

import os
import sys

IS_A_TTY = sys.stdout.isatty()

class Maker:
    RESET = '\x1b[39m'
    def __init__(self, code):
        self.COLOR = code
    def __add__(self, item):
        global IS_A_TTY
        if not IS_A_TTY:
            return str(item)
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

def color_filepath(filepath):
    import os.path
    dirname = Code.LIGHTBLACK_EX + (os.path.dirname(filepath) + os.path.sep)
    basename = Code.LIGHTCYAN_EX + os.path.basename(filepath)
    result = dirname + basename 
    return result


def print_samples():
    from waivek.reltools import rel2abs
    filepath = rel2abs("item.txt")
    # print(color_filepath(filepath))
    # return
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

def supports_color():
    # from django
    """
    Return True if the running system's terminal supports color,
    and False otherwise.
    """

    def vt_codes_enabled_in_windows_registry():
        """
        Check the Windows Registry to see if VT code handling has been enabled
        by default, see https://superuser.com/a/1300251/447564.
        """
        try:
            # winreg is only available on Windows.
            import winreg
        except ImportError:
            return False
        else:
            try:
                reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Console")
                reg_key_value, _ = winreg.QueryValueEx(reg_key, "VirtualTerminalLevel")
            except FileNotFoundError:
                return False
            else:
                return reg_key_value == 1

    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

    return is_a_tty and (
        sys.platform != "win32"
        or "ANSICON" in os.environ
        or
        # Windows Terminal supports VT codes.
        "WT_SESSION" in os.environ
        or
        # Microsoft Visual Studio Code's built-in terminal supports colors.
        os.environ.get("TERM_PROGRAM") == "vscode"
        or vt_codes_enabled_in_windows_registry()
    )

def enable_cmd_color_windows_10_1607():
    # Black magic!
    # https://stackoverflow.com/a/39675059

    # To enable: https://superuser.com/questions/413073/windows-console-with-ansi-colors-handling
    # Go to regedit
    #
    # dword is 32-bit
    # [HKEY_CURRENT_USER\Console]
    # "VirtualTerminalLevel"=dword:00000001
    #
    return
    if supports_color() is False:
        os.system('') #enable VT100 Escape Sequence for WINDOWS 10 Ver. 1607
        timer.start("import ctypes")
        from ctypes import windll
        timer.print("import ctypes")
        windll.kernel32.SetConsoleMode(windll.kernel32.GetStdHandle(-11), 7)

enable_cmd_color_windows_10_1607()

if __name__ == "__main__":
    print_samples()

