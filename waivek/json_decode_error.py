

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from json import JSONDecodeError

def handle_json_decode_error(error: "JSONDecodeError"):

    # raise JSONDecodeError("\\uXXXX escape", s, pos)
    # raise JSONDecodeError("Unterminated string starting at", s, begin)
    # raise JSONDecodeError("Invalid control character {0!r} at".format(terminator), s, end)
    # raise JSONDecodeError("Unterminated string starting at",
    # raise JSONDecodeError("Invalid \\escape: {0!r}".format(esc), s, end)
    # raise JSONDecodeError("Expecting property name enclosed in double quotes", s, end)
    # raise JSONDecodeError("Expecting ':' delimiter", s, end)
    # raise JSONDecodeError("Expecting value", s, err.value) from None
    # raise JSONDecodeError("Expecting ',' delimiter", s, end - 1)
    # raise JSONDecodeError("Expecting property name enclosed in double quotes", s, end - 1)
    # raise JSONDecodeError("Expecting value", s, err.value) from None
    # raise JSONDecodeError("Expecting ',' delimiter", s, end - 1)
    # raise JSONDecodeError("Extra data", s, end)
    # raise JSONDecodeError("Expecting value", s, err.value) from None

    message = error.args
    arg = error.doc
    colno = error.colno
    lineno = error.lineno
    charpos = error.pos
    msg = error.msg
    from waivek.color import Code
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.theme import Theme
    from rich.style import Style
    from rich.text import Text
    console = Console(highlight=False, record=True)
    error_string = arg
    error_lines = error_string.split("\n")
    error_line_saved = error_lines[lineno-1]
    inline_error_message = " ■ " + msg
    inline_error_message = "╰─ " + message[0]
    # error_lines[lineno-1] = error_lines[lineno-1] + inline_error_message
    error_string_with_inlined_message = "\n".join(error_lines)

    theme = "monokai"
    syntax = Syntax(error_string_with_inlined_message, "json", theme=theme, line_numbers=True, highlight_lines={lineno}, padding=0)
    bgcolor = syntax.get_theme(theme).get_background_style()
    assert bgcolor.bgcolor
    style = Style(color='#ff0000', bold=True, bgcolor=bgcolor.bgcolor)
    # syntax.stylize_range(style, (lineno, len(error_line_saved)), (lineno, len(error_line_saved) + len(inline_error_message)))

    with console.capture() as capture:
        console.print(syntax)
    string = capture.get()
    lines = string.split("\n")
    with console.capture() as capture:
        leading_space_count = len("❱ ") + len(str(lineno)) + colno
        console.print(" " * leading_space_count + inline_error_message, end="", style=style)
    insert_line = capture.get()
    lines.insert(lineno,  insert_line)

    # x = 3
    range_num = 10
    range_start = lineno - range_num if lineno - range_num > 0 else 0
    range_end = lineno + range_num if lineno + range_num < len(lines) else len(lines) + 1

    lines = lines[range_start:range_end]
    lines = "\n".join(lines)
    print(lines, end="")

def handle_multiple_json_decode_errors():
    import json
    # variables {{{
    string = """
    {
        'a': 1
        }"""

    faulty_json_strings = [
        # "\\uXXXX escape"
        """
        "\\u123G"
        """,  # Invalid Unicode escape sequence

        # "Unterminated string starting at"
        """
        "incomplete string
        """,  # String not closed

        # "Invalid control character {0!r} at"
        """
        "invalid\x1Fcharacter"
        """,  # Contains an invalid control character

        # "Unterminated string starting at"
        """
        {
            "key": "value
        }
        """,  # String not closed in a key-value pair

        # "Invalid \\escape: {0!r}"
        """
        "invalid\\escape"
        """,  # Invalid escape sequence

        # "Expecting property name enclosed in double quotes"
        """
        {
            key: "value"
        }
        """,  # Key not enclosed in double quotes

        # "Expecting ':' delimiter"
        """
        {
            "key" "value"
        }
        """,  # Missing colon between key and value

        # "Expecting value"
        """
        {
            "key":
        }
        """,  # Missing value after the colon

        # "Expecting ',' delimiter"
        """
        {
            "key1": "value1"
            "key2": "value2"
        }
        """,  # Missing comma between key-value pairs

        # "Expecting property name enclosed in double quotes"
        """
        {
            123: "value"
        }
        """,  # Property name is a number, not enclosed in double quotes

        # "Expecting value"
        """
        {
            "key": null,
            "another_key":
        }
        """,  # Missing value after the colon

        # "Expecting ',' delimiter"
        """
        {
            "key": "value"
            "another_key": "value"
        }
        """,  # Missing comma between key-value pairs

        # "Extra data"
        """
        {
            "key": "value"
        }
        extra
        """,  # Extra data after valid JSON

        # "Expecting value"
        """
        {
            "key": "value",
            "another_key":
        }
        """,  # Missing value after the colon
    ]
    def generate_faulty_json():
        data = {
            "users": [
                {"id": i, "name": f"User_{i}", "email": f"user_{i}@example.com"} for i in range(1, 100)
            ]
        }
        data["users"].append({"id": 100, "name": "User_100", "email": "user_100@example.com"})

        for i in range(101, 200):
            data["users"].append({"id": i, "name": f"User_{i}", "email": f"user_{i}@example.com"})

        json_string = json.dumps(data, indent=4)
        lines = json_string.split('\n')

        lines[99] = lines[99].replace('User_100', 'User_100').replace(',', '')

        return '\n'.join(lines)
        # return ''.join(lines)
    # }}}

    for i, faulty_json_string in enumerate([*faulty_json_strings, string, generate_faulty_json()]):
        try:
            json.loads(faulty_json_string)
        except json.JSONDecodeError as error:
            handle_json_decode_error(error)
            print()
    big_string = generate_faulty_json()

def main():
    handle_multiple_json_decode_errors()

if __name__ == "__main__":
    main()

