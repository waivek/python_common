import os
import re
from common import enumerate_count
from ic import ic
from truncate import get_display_length
from truncate import truncate as t1
from ai_truncate import truncate as t2

def special_cases():

    combining_char = "e\u0301"  # 'e' followed by a combining acute accent (U+0301)
    print(combining_char)  # Output: é

    zero_width = "hello\u200Bworld"  # zero-width space between 'hello' and 'world'
    zero_width_joiner = "👨\u200D👩\u200D👧\u200D👦"  # family emoji using zero-width joiners
    print(zero_width)  # Output: helloworld (looks normal, but there's an invisible character)
    print(zero_width_joiner)  # Output: 👨‍👩‍👧‍👦 (family emoji)

    wide_character = "😊"  # This emoji is a wide character (2 column width)
    narrow_character = "a"  # Regular characters like 'a' are narrow (1 column width)

    composed = "\u00E9"  # 'é' as a single character (U+00E9)
    decomposed = "e\u0301"  # 'e' followed by combining acute accent (U+0301)
    print(composed == decomposed)  # Output: False (they look the same but are different strings)

def normalize_ansi_order(string):
    return string
    from truncate import tokenize_string
    tokens = tokenize_string(string)
    return_string = ""
    for token in tokens:
        value = token.value
        value_without_ansi = re.sub(r"\033\[[0-9;]*m", "", value)
        ansi_codes = re.findall(r"\033\[[0-9;]*m", value)
        ansi_codes.sort()
        value_with_sorted_ansi = "".join(ansi_codes) + value_without_ansi
        return_string += value_with_sorted_ansi
    if string != return_string:
        print(f"[normalize_ansi_order] Original: {repr(string)}")
        print(f"[normalize_ansi_order] Sorted  : {repr(return_string)}")
        print()
    return return_string

def get_test_cases():
    # test_cases = [ ... ] {{{
    test_cases = [
        # Basic case without any special characters
        ("Hello, World!", 5, "H...!"),
        ("Hello, World!", 12, "Hello, World!"),

        # Case with ANSI codes that shouldn't count towards length
        ("Hello \033[31mWorld\033[0m!", 10, "Hel...ld!"),

        # Case with combining characters
        ("Hello\u0301", 4, "Hel..."),

        # Case with zero-width space
        ("Hello\u200B World", 8, "He...ld"),

        # Case with emojis (display length 1 for each emoji)
        ("Hello 🌍", 7, "Hel..."),

        # Case with longer string that needs truncation
        ("This is a long string that will be truncated", 20, "This...uncated"),

        # Case where the length matches the input string
        ("Short string", 12, "Short string"),

        # Complex case with ANSI, combining characters, and emoji
        ("Hello \033[31mWorld\u0301 🌍\033[0m!", 10, "Hel...🌍!"),

        ("你好，世界", 3, "你..."),  # Chinese string, truncated

        ("こんにちは、世界", 5, "こん..."),  # Japanese string, truncated

        ("Hello 你好 こんにちは", 10, "Hel...ちは"),  # Mixed English, Chinese, Japanese, truncated

        ("你好，世界 🌏", 4, "你...🌏"),  # Chinese with emoji, truncated

        ("こんにちは、世界 🌍", 6, "こん...🌍"),  # Japanese with emoji, truncated

        ("Hello 你好 \033[31mこんにちは 🌏\033[0m!", 12, "Hel...🌏!"),  # Mixed with ANSI code and emoji, truncated

        ("Hello \033[31mWorld with a reset code that gets truncated\033[0m as we go along.", 20, "FOO"),

        ("Hello World with a reset code that gets truncated as we go along.", 20, "FOO"),

        ("Hello World with a reset code that gets truncated as we go along.", 3, "FOO"),

        ("Hello \033[31mWorld\033[0m!", 10, "FOO"),

        ("👨‍👩‍👧‍👦 Family"            ,  5 , "👨‍👩‍👧‍👦...")   , # Complex emoji (should count as one character)
        ("H\u0065\u0301llo"                             ,  3 , "Hé...")                           , # Combining characters
        ("Héllo\nWorld"                                 ,  7 , "Héll...")                         , # Newline character
        ("Tab\tcharacter"                               ,  6 , "Tab...")                          , # Tab character
        ("Mixed\twhitespace \ncharacters"               , 10 , "Mixed\t...")                      , # Mixed whitespace
        ("\033[1mBold\033[0m \033[3mItalic\033[0m"      ,  8 , "\033[1mBol...\033[0m")            , # Multiple ANSI codes
        ("\033[38;5;10mColored\033[0m text"             , 10 , "\033[38;5;10mColo...\033[0m")     , # 8-bit color ANSI code
        ("\033[48;2;255;0;0mRGB\033[0m background"      ,  7 , "\033[48;2;255;0;0mRGB...\033[0m") , # 24-bit color ANSI code
        ("ASCII art: ┌─┐\n│ │\n└─┘"                     , 15 , "ASCII art: ┌...")                 , # ASCII art
        ("Über für"                                     ,  5 , "Übe...")                          , # Non-ASCII characters
        ("अ ऑ इ ई उ ऊ"                                  ,  4 , "अ ...")                           , # Devanagari script
        ("سلام دنیا"                                     ,  5 , "سلا...")                           , # Right-to-left text (Arabic)
        ("\u200Ezero-width\u200F"                       ,  8 , "\u200Ezer...\u200F")              , # Zero-width characters
        ("Normal \x1b[31mred\x1b[0m \x1b[1mbold\x1b[0m" , 10 , "Normal \x1b[31mre...\x1b[0m")     , # ANSI codes mid-string

        ("🎨\033[38;5;208m🖌️\033[0m🎭", 4, "🎨🖌️..."),  # Emojis with ANSI color codes
        ("文字化け", 4, "文字..."),  # CJK characters
        ("🇺🇸🇬🇧🇫🇷", 4, "🇺🇸🇬🇧..."),  # Flag emojis
        ("Hello World!", 4, "Hel..."),  # Basic Latin characters

        # ("\033[1m..........\033[0m", 5, "....."), # Ten periods
    ]
    # }}}
    return test_cases

def compare_truncate_implementations(truncate1, truncate2):
    truncate1_tag = f"{os.path.basename(truncate1.__code__.co_filename)}:{truncate1.__name__}()"
    truncate2_tag = f"{os.path.basename(truncate2.__code__.co_filename)}:{truncate2.__name__}()"
    just_int = max(len(truncate1_tag), len(truncate2_tag))
    test_cases = get_test_cases()
    for count_string, (input_string, max_length, expected_output) in enumerate_count(test_cases):
        index = count_string[1:-1].split("/")[0]
        result1 = truncate1(input_string, max_length)
        result2 = truncate2(input_string, max_length)
        if result1 != result2:
            print(f"\n\033[1;30;41m FAIL \033[0m Test {index}")
        else:
            print(f"\n\033[1;30;42m PASS \033[0m Test {index}")

        if result1 != result2:
            print(f"max_length: {max_length}")
            print(f"{'Input'.ljust(just_int)}: {repr(input_string)}")
            print(f"{truncate1_tag.ljust(just_int)}: {repr(result1)}")
            print(f"{truncate2_tag.ljust(just_int)}: {repr(result2)}")
            print(f"{'Input'.ljust(just_int)}:  {input_string}")
            print(f"{truncate1_tag.ljust(just_int)}:  {result1}")
            print(f"{truncate2_tag.ljust(just_int)}:  {result2}")
            print()


def test_truncate():
    """
    Test cases to validate the correctness of the truncate function.
    """
    from truncate import truncate
    test_cases = get_test_cases()

    assertion_failures = []
    for count_string, (input_string, max_length, expected_output) in enumerate_count(test_cases):
        indent = " " * 4
        index = count_string[1:-1].split("/")[0]
        print(f"\n\033[1;30;44m TEST \033[0m \033[1m{count_string}\033[0m\n")

        print(indent + f"max_length      = {max_length}")
        print(indent + f"Input  (len:{get_display_length(input_string):2d}) = `{repr(input_string)[1:-1]}`")
        result = truncate(input_string, max_length)
        print(indent + f"Result (len:{get_display_length(result):2d}) = `{repr(result)[1:-1]}`")
        print(indent + "marker          = `" + "|" * max_length + "`")
        print(indent + "truncated       = `" + result + "`")
        print(indent + "repr(truncated) = `" + repr(result)[1:-1] + "`")
        if "..." in result:
            separator_regex_with_ansi = re.compile(r"((\033\[[0-9;]*m)*)\.\.\.((\033\[[0-9;]*m)*)")
            separator_regex_with_ansi = re.compile(r"(\033\[[0-9;]*m)*\.\.\.(\033\[[0-9;]*m)*")

            before_separator, _, _, after_separator = re.split(separator_regex_with_ansi, result)
            try:
                # assert normalize_ansi_order(input_string).startswith(normalize_ansi_order(before_separator))
                assert input_string.startswith(before_separator), "startswith"
            except AssertionError as error:
                print(f"\033[31mFAIL: {error}\033[0m")
                print(f"Expected: {repr(normalize_ansi_order(input_string))}")
                print(f"Got     : {repr(normalize_ansi_order(before_separator))}")
                print()
                assertion_failures.append(index)
            try:
                # assert normalize_ansi_order(input_string).endswith(normalize_ansi_order(after_separator))
                assert input_string.endswith(after_separator), "endswith"
            except AssertionError as error:
                print(f"\033[31mFAIL: {error}\033[0m")
                print(f"Expected: {repr(normalize_ansi_order(input_string))}")
                print(f"Got     : {repr(normalize_ansi_order(after_separator))}")
                print()
                assertion_failures.append(index)
        print("\n" + indent + f"\033[1;30;42m PASS \033[0m `{input_string}` truncated to length {max_length}")
    if assertion_failures:
        print("\n\033[1;31mASSERTION FAILURES: \033[0m" + ", ".join([f"Test {index}" for index in assertion_failures]) + "\n")

compare_truncate_implementations(t1, t2)

# test_truncate()

# run.vim: term ++rows=80 python %

