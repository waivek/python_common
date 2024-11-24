# read: https://github.com/Delgan/loguru and structlog
from tzlocal import get_localzone
from datetime import datetime
import sys
import os.path

def get_date_tag() -> str:
    zoneinfo = get_localzone()
    dt = datetime.now(zoneinfo).replace(microsecond=0)
    return dt.isoformat()

def get_file_tag() -> str:
    try:
        frame = sys._getframe(2) # 0 is get_file_tag, 1 is the function in this file, 2 is the caller
    except ValueError:
        return f"\x1b[38;5;8m{os.path.basename(__file__)}\x1b[0m No caller found"
    filename = frame.f_code.co_filename
    line_number = frame.f_lineno
    return f"{os.path.basename(filename)}:{line_number}"

def log(*args, **kwargs):
    print(get_date_tag(), get_file_tag(), *args, **kwargs)

def main():
    from box.ic import ic
    date_tag = get_date_tag()
    file_tag = get_file_tag()
    print(f"{date_tag} {file_tag}")

if __name__ == "__main__":
    main()

