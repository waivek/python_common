from waivek.error2 import handler

from enum import Enum
import re
from typing import List, Optional
from waivek import ic

class TokenType(Enum):
    CHARACTER = "character"
    ANSI_CODE = "ansi_code"
    EMOJI = "emoji"
    COMBINING_CHAR = "combining_char"
    ZERO_WIDTH_SPACE = "zero_width_space"

class Token:

    def __init__(self, value: str, token_type: TokenType, display_length: int, ansi_reset_code: Optional[str] = None, active_ansi_codes: Optional[List[str]] = None):
        self.value = value  # Raw value of the token (e.g., a character, emoji, or ANSI code)
        self.token_type = token_type  # Type of the token (character, ANSI code, etc.)
        self.display_length = display_length  # Displayed length of the token (0 for ANSI, combining chars, etc.)
        self.ansi_reset_code = ansi_reset_code  # Optional ANSI reset code
        self.active_ansi_codes = active_ansi_codes if active_ansi_codes is not None else []  # List of active ANSI codes

    def __repr__(self):
        return f"Token(value={repr(self.value)}, type={self.token_type}, length={self.display_length}, active_ansi_codes={self.active_ansi_codes})"


def tokenize_string(string: str) -> List[Token]:
    """
    Break a string into tokens based on ANSI codes, emojis, combining characters, etc.
    Track multiple active ANSI codes.
    """
    tokens = []
    ansi_code_pattern = re.compile(r'\x1b\[[0-9;]*m')
    emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F]')
    active_ansi_codes = []  # To track the list of active ANSI codes

    index = 0
    while index < len(string):
        # Match ANSI code
        ansi_match = ansi_code_pattern.match(string, index)
        if ansi_match:
            ansi_code = ansi_match.group()

            # If it's a reset code, clear active ANSI codes
            if ansi_code == '\033[0m':
                active_ansi_codes.clear()
            else:
                # Add the current ANSI code to the list of active codes
                active_ansi_codes.append(ansi_code)

            # Add the ANSI code token with current active codes
            tokens.append(Token(ansi_code, TokenType.ANSI_CODE, 0, ansi_reset_code='\033[0m', active_ansi_codes=list(active_ansi_codes)))
            index += len(ansi_match.group())
            continue

        char = string[index]

        # Handle zero-width spaces
        if char == '\u200B':
            tokens.append(Token(char, TokenType.ZERO_WIDTH_SPACE, 0, active_ansi_codes=list(active_ansi_codes)))

        # Handle combining characters
        elif re.match(r'[\u0300-\u036F]', char):
            tokens.append(Token(char, TokenType.COMBINING_CHAR, 0, active_ansi_codes=list(active_ansi_codes)))

        # Handle emojis
        elif emoji_pattern.match(char):
            tokens.append(Token(char, TokenType.EMOJI, 1, active_ansi_codes=list(active_ansi_codes)))

        # Handle regular characters
        else:
            tokens.append(Token(char, TokenType.CHARACTER, 1, active_ansi_codes=list(active_ansi_codes)))

        index += 1

    return tokens

def truncate(string: str, max_length: int) -> str:
    """
    Truncate the tokens to fit within the max length, handling complex characters properly.
    Ensure ANSI codes are preserved correctly and closed with a reset code.
    """
    tokens = tokenize_string(string)
    total_display_length = sum(token.display_length for token in tokens)

    # If the total display length is already less than or equal to max_length, return the original string
    if total_display_length <= max_length:
        return ''.join(token.value for token in tokens)
    
    middle_string = "..."
    middle_length = len(middle_string)
    remaining_length = max_length - middle_length
    
    # Adjust remaining length if it's odd
    left_display_length = remaining_length // 2
    right_display_length = remaining_length - left_display_length

    left_tokens, right_tokens = [], []
    current_display_length = 0
    
    # Collect tokens from the left side
    for token in tokens:
        if current_display_length + token.display_length > left_display_length:
            break
        left_tokens.append(token)
        current_display_length += token.display_length
    
    current_display_length = 0
    
    # Collect tokens from the right side
    for token in reversed(tokens):
        if current_display_length + token.display_length > right_display_length:
            break
        right_tokens.append(token)
        current_display_length += token.display_length
    
    right_tokens.reverse()  # We reversed earlier, so we need to reverse back
    
    # Combine left slice, middle string, and right slice
    final_tokens = left_tokens + [Token(middle_string, TokenType.CHARACTER, middle_length)] + right_tokens

    final_string = ''.join(token.value for token in left_tokens) + middle_string

    if left_tokens and left_tokens[-1].active_ansi_codes:
        final_string +=  "\033[0m"

    if right_tokens and right_tokens[0].active_ansi_codes:
        final_string += ''.join(ansi_code for ansi_code in right_tokens[0].active_ansi_codes)

    final_string += ''.join(token.value for token in right_tokens)

    if final_tokens and final_tokens[-1].active_ansi_codes:
        final_string += "\033[0m"
    # Combine (end)
    
    # Recalculate the final display length and ensure it's correct
    final_display_length = get_display_length(final_string)
    if final_display_length != max_length:
        # Adjust the string by removing characters from the right if the length is off
        if final_display_length > max_length:
            excess_length = final_display_length - max_length
            final_string = final_string[:-excess_length]
        raise ValueError(f"Truncated string has display length {final_display_length}, expected {max_length}")

    return final_string

def get_display_length(string, verbose=False) -> int:
    """
    Get the display length of a string, handling ANSI codes, emojis, combining characters, etc.
    """
    tokens = tokenize_string(string)
    if verbose:
        for token in tokens:
            print(token)
    return sum(token.display_length for token in tokens)

def print_truncate_or_raise(string, length):
    truncated = truncate(string, length)
    assert get_display_length(truncated) <= length, f"Expected {length}, got {get_display_length(truncated)}"
    print("string          = `" + string + "`")
    print("marker          = `" + "|" * length + "`")
    print("truncated       = `" + truncated + "`")
    print("repr(truncated) = `" + repr(truncated)[1:-1] + "`")
    print()

def main():
    # Example usage
    input_string = "Hello \033[31mWorld\033[0m combining\u0301 and zero-width"
    input_string = "Hello, World!"

    input_string3 = "Hello \033[31mWorld with a reset code that gets truncated\033[0m as we go along."
    input_string4 = "Hello World with a reset code that gets truncated as we go along."

    LENGTH = 20

    with handler():
        print_truncate_or_raise(input_string3, LENGTH)
        print_truncate_or_raise(input_string4, LENGTH)
        print_truncate_or_raise(input_string4, 3)
        input_string5 = "Hello \033[31mWorld\033[0m!"
        truncate(input_string5, 10)
        print_truncate_or_raise(input_string5, 10)
        input_string5 = "Hello \033[31mWorld!\033[0m"
        truncate(input_string5, 10)
        print_truncate_or_raise(input_string5, 10)

if __name__ == "__main__":
    main()

