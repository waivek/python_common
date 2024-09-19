import re

def truncate(s, max_length):
    ansi_escape = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')
    
    # Tokenize the string into (text, is_visible, styles) tuples
    tokens = []
    pos = 0
    active_styles = []
    while pos < len(s):
        m = ansi_escape.match(s, pos)
        if m:
            code = m.group()
            if code == '\x1b[0m':
                # Reset code clears all styles
                active_styles.clear()
            else:
                # Add style to active styles
                active_styles.append(code)
            tokens.append((code, False, code))
            pos = m.end()
        else:
            # Visible character
            tokens.append((s[pos], True, ''.join(active_styles)))
            pos += 1

    # Calculate the visible length (excluding ANSI codes)
    visible_length = sum(1 for t, is_visible, _ in tokens if is_visible)

    # If the visible length is within the maximum, return the original string
    if visible_length <= max_length:
        return s

    separator = "..."
    sep_len = len(separator)
    visible_chars_to_keep = max_length - sep_len

    if visible_chars_to_keep <= 0:
        # Not enough space even for the separator and any chars
        return separator[:max_length]

    # **Prioritize the right side (end of the string)**
    # Split the visible characters between the start and end
    start_visible_chars = visible_chars_to_keep // 2
    end_visible_chars = visible_chars_to_keep // 2 + visible_chars_to_keep % 2

    # Collect tokens from the start
    start_tokens = []
    visible_count = 0
    i = 0
    while i < len(tokens):
        t, is_visible, styles = tokens[i]
        start_tokens.append((t, is_visible, styles))
        if is_visible:
            visible_count += 1
            if visible_count >= start_visible_chars:
                # Include any subsequent ANSI codes
                i += 1
                while i < len(tokens) and not tokens[i][1]:
                    start_tokens.append(tokens[i])
                    i += 1
                break
        i += 1
    # Save the active styles at the truncation point
    active_styles_start = tokens[i-1][2] if i > 0 else ''

    # Collect tokens from the end
    end_tokens = []
    visible_count = 0
    i = len(tokens) - 1
    while i >= 0:
        t, is_visible, styles = tokens[i]
        end_tokens.insert(0, (t, is_visible, styles))
        if is_visible:
            visible_count += 1
            if visible_count >= end_visible_chars:
                # Include any preceding ANSI codes
                i -= 1
                while i >= 0 and not tokens[i][1]:
                    end_tokens.insert(0, tokens[i])
                    i -= 1
                break
        i -= 1
    # Save the active styles at the start of the end tokens
    active_styles_end = end_tokens[0][2] if end_tokens else ''

    # Close any open styles before the separator
    reset_code = '\x1b[0m'
    if active_styles_start and not start_tokens[-1][0].endswith(reset_code):
        start_tokens.append((reset_code, False, ''))

    # Re-open styles after the separator if needed
    if active_styles_end:
        end_tokens.insert(0, (active_styles_end, False, active_styles_end))

    # Combine the tokens with the separator
    truncated_tokens = start_tokens + [(separator, True, '')] + end_tokens

    # Reconstruct the string
    result = ''.join(t for t, is_visible, _ in truncated_tokens)
    return result

# run.vim: vert term python test_truncate.py
