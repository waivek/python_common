# Prompt:
#
#   write me a python function called markup that replicates a subset of the rich python library coloring features. i basically want these tests to pass:
# 
#     tests = [
#         "[green bold italic]Hi[/] [bright_black]Bye[/]",
#         "[green]Hello[/] [bold]World[/]",
#         "[italic red]Test[/]",
#         "[red bold][Hello][/]",
#         "[black on red bold] MISSING [/]"
#     ]
#
# it should return a marked up ansi string
# 
# handle this edge case:
#
#         "[red bold][Hello[/]",
#
# output should be [Hello in red bold
#
# also handle this case:
#
#      "[black on red bold] MISSING [/]"
#
# in the output, the background should be red, foreground should be black and the text should be bold

def markup(s):
    style_codes = {
        'bold': '1',
        'italic': '3',
        'underline': '4',
    }

    fg_color_codes = {
        'black': '30',
        'red': '31',
        'green': '32',
        'yellow': '33',
        'blue': '34',
        'magenta': '35',
        'cyan': '36',
        'white': '37',
        'bright_black': '90',
        'bright_red': '91',
        'bright_green': '92',
        'bright_yellow': '93',
        'bright_blue': '94',
        'bright_magenta': '95',
        'bright_cyan': '96',
        'bright_white': '97',
    }

    bg_color_codes = {
        'black': '40',
        'red': '41',
        'green': '42',
        'yellow': '43',
        'blue': '44',
        'magenta': '45',
        'cyan': '46',
        'white': '47',
        'bright_black': '100',
        'bright_red': '101',
        'bright_green': '102',
        'bright_yellow': '103',
        'bright_blue': '104',
        'bright_magenta': '105',
        'bright_cyan': '106',
        'bright_white': '107',
    }

    result = ''
    i = 0
    length = len(s)
    while i < length:
        if s[i] == '[':
            if i + 1 < length and s[i + 1] != '/':
                # Potential opening tag
                i_end = s.find(']', i + 1)
                if i_end == -1:
                    # No closing ']', treat as literal '['
                    result += s[i]
                    i += 1
                    continue
                # Extract styles
                styles_str = s[i + 1:i_end]
                styles = styles_str.strip().split()
                codes = []
                valid_tag = False
                idx = 0
                while idx < len(styles):
                    style = styles[idx]
                    if style == 'on':
                        idx += 1
                        if idx < len(styles):
                            bg_color = styles[idx]
                            if bg_color in bg_color_codes:
                                codes.append(bg_color_codes[bg_color])
                                valid_tag = True
                            else:
                                # Invalid background color, ignore
                                pass
                        else:
                            # 'on' at end with no color, ignore
                            pass
                    elif style in style_codes:
                        codes.append(style_codes[style])
                        valid_tag = True
                    elif style in fg_color_codes:
                        codes.append(fg_color_codes[style])
                        valid_tag = True
                    else:
                        # Unknown style, ignore
                        pass
                    idx += 1
                if valid_tag:
                    escape_sequence = '\033[' + ';'.join(codes) + 'm'
                    result += escape_sequence
                    i = i_end + 1
                else:
                    # Not a valid tag, treat '[' as literal
                    result += s[i]
                    i += 1
            elif i + 1 < length and s[i + 1] == '/':
                # Closing tag
                if i + 2 < length and s[i + 2] == ']':
                    # Valid closing tag
                    result += '\033[0m'
                    i += 3
                else:
                    # Invalid closing tag, treat as literal '['
                    result += s[i]
                    i += 1
            else:
                # Invalid tag or standalone '[', treat as literal
                result += s[i]
                i += 1
        else:
            # Regular character
            result += s[i]
            i += 1
    return result


if __name__ == "__main__":
    tests = [
        "[green bold italic]Hi[/] [bright_black]Bye[/]",
        "[green]Hello[/] [bold]World[/]",
        "[italic red]Test[/]",
        "[red bold][Hello][/]",
        "[black on red bold] MISSING [/] [blue]What is wrong?[/] [yellow]Nothing...[/]"
    ]
    
    for test in tests:
        result = markup(test)
        print("\nINPUT     :", test)
        print("RAW       :", repr(result))
        print("FORMATTED :", result)
