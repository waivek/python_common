from waivek import Timer   # Single Use
timer = Timer()
from waivek import Code    # Multi-Use
from waivek import handler # Single Use
from waivek import ic, ib     # Multi-Use, import time: 70ms - 110ms
from waivek import rel2abs

from typing import Literal, Union
from colorama import init, Fore, Back, Style
init(autoreset=True)

def print_color():
    # print_color {{{

    # background can be (light)red|blue|green(_ex)
    # foreground can be black|lightwhite_ex


    def print_color(text: str, background: str, foreground: Literal['black', 'lightwhite_ex']='black') -> None:
        foreground_color = getattr(Fore, foreground.upper())
        background_color = getattr(Back, background.upper())
        print(f'{foreground_color}{background_color} {text} ')

    # Test

    tuples = [ ('FAIL', 'red'),
              ('ENSURE', 'blue'),
              ('PASS', 'green'),
              ('WARN', 'yellow'),
              ('INFO', 'cyan'),
              ('DEBUG', 'magenta'),
              ('TRACE', 'lightwhite_ex') ]

    print()
    for string, color in tuples:
        print_color(string, color)
        print()
    # }}}
                    
def print_color_lister():
    # print_color_lister {{{
    backgrounds = [
            ('Back.LIGHTRED_EX', Back.LIGHTRED_EX),
            ('Back.LIGHTBLUE_EX', Back.LIGHTBLUE_EX),
            ('Back.LIGHTGREEN_EX', Back.LIGHTGREEN_EX),
            ('Back.YELLOW', Back.YELLOW),
            ('Back.LIGHTYELLOW_EX', Back.LIGHTYELLOW_EX)
    ]

    foregrounds = [
            ('Fore.BLACK', Fore.BLACK),
            ('Fore.LIGHTWHITE_EX', Fore.LIGHTWHITE_EX)
    ]

    styles = [
            ('Style.BRIGHT', Style.BRIGHT),
            ('Style.NORMAL', Style.NORMAL),
            ('Style.DIM', Style.DIM)
    ]

    for bg_name, bg in backgrounds:
        for fg_name, fg in foregrounds:
            for style_name, style in styles:
                lhs = bg + fg + style + ' OK '
                rhs = " ".join([bg_name, fg_name, style_name])
                print(lhs, rhs)
    # }}}

def experiments():
    from rich import print # doesn’t play well with coloroma init(autoreset=True)
    # experiments {{{

    color = "#FF0000"
    pink = "#FF00FF"
    light_red = "#FF7F7F"
    light_green = "#7FFF7F"
    green = "#00FF00"
    colors = [ light_red, light_green, green, pink, "magenta", "blue", "red", "yellow", "green" ]
    length = max(len(color) for color in colors)
    for color in colors:
        # print(f"{color}: [#FFFFFF bold on {color}] OK [/#FFFFFF bold on {color}]!")
        # print(f"{color}: [#000000 bold on {color}] OK [/#000000 bold on {color}]!")
        # do above but with padding on {color} of 10
        print("{color:{width}s}: [#FFFFFF bold on {color}] OK [/#FFFFFF bold on {color}]".format(color=color, width=length))
        print("{color:{width}s}: [#000000 bold on {color}] OK [/#000000 bold on {color}]".format(color=color, width=length))
    # }}}

def main():
    experiments()
    print_color_lister()
    print_color()

if __name__ == "__main__":
    with handler():
        main()

