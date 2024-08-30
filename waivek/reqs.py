from waivek.timer import Timer   # Single Use
timer = Timer()
from waivek.color import Code    # Multi-Use
from waivek.error import handler # Single Use
from waivek.ic import ic, ib     # Multi-Use, import time: 70ms - 110ms
Code; ic; ib; handler
from waivek.reltools import rel2abs

def main():
    # print_python_modules()
    # print()
    # print_pipreqs()
    pypi_version()

def pypi_version():
    from waivek.ic import ic
    import requests
    package_name = "waivek"
    url = f"https://pypi.org/pypi/{package_name}/json"
    resp = requests.get(url)
    D = resp.json()
    version = D["info"]["version"]
    major, minor, patch = version.split(".")
    patch = int(patch) + 1
    new_version = f"V- {major}.{minor}.{patch}"
    ic(new_version)
    


def print_python_modules():
    import os.path
    to_module_name = lambda path: os.path.splitext(os.path.basename(path))[0]
    helper_modules = [ 'frame.py', 'trace.py' ]
    ignore_modules = [ 'reqs.py', 'setup.py', 'tdd.py', 'template.py', 'test.py' ]
    py_modules = [ to_module_name(module) for module in get_python_files() if module not in ignore_modules ]
    print(f"py_modules = {py_modules}")
    print("# [print_python_modules] see helper_modules and ignore_modules for ignored python files")

def print_pipreqs():
    import subprocess
    current_dir = rel2abs(".")
    command = ["pipreqs", "--print", current_dir ]
    print("$ " + " ".join(command))
    result_binary = subprocess.run(command, capture_output=True)
    contents = result_binary.stdout.decode("utf-8").strip()
    lines = contents.split("\n")
    table = []
    manual_lines = [
        'pysqlite3-binary; platform_system=="Linux"'
    ]
    required_packages = {
        "aiohttp": "get.py",
        "executing": "ic.py",
        "python_dateutil": "common.py",
        "timeago": "common.py"
    }
    ignore_packages = {
        "ipdb": "error.py",
        "pysqlite3": "db.py"
    }
    for line in lines:
        package, version = line.split("==")
        table.append({ "package": package, "version": version })

    install_requires_lines = []
    for D in table:
        package = D['package']
        version = D['version']
        if package in required_packages:
            print(Code.GREEN + package)
            line = f"{package}=={version}"
            install_requires_lines.append(line)
        elif package in ignore_packages:
            print(Code.LIGHTBLACK_EX + (package + "# ignore"))
        else:
            print(Code.RED + package)
    lines = install_requires_lines + manual_lines
    lines = [ line.strip() for line in lines ]
    lines = [ f"'{line}'" for line in lines ]
    lines = [ f"        {line}" for line in lines ]
    print("    install_requires = [")
    print(",\n".join(lines))
    print("    ]")


            
        


def get_directories():
    from glob import glob
    import os.path
    current_dir = rel2abs(".")
    paths = glob(os.path.join(current_dir, "**/"), recursive=True)
    relpaths = [ os.path.relpath(path, current_dir) for path in paths ]
    return relpaths

def get_non_python_files():
    from glob import glob
    import os.path
    current_dir = rel2abs(".")
    paths = glob(os.path.join(current_dir, "*"), recursive=False)
    paths = [ path for path in paths if os.path.isfile(path) ]
    relpaths = [ os.path.relpath(path, current_dir) for path in paths ]
    relpaths = [ path for path in relpaths if not path.endswith(".py") ]
    return relpaths

def get_python_files():
    from glob import glob
    import os.path
    current_dir = rel2abs(".")
    paths = glob(os.path.join(current_dir, "**/*.py"), recursive=True)
    relpaths = [ os.path.relpath(path, current_dir) for path in paths ]
    return relpaths

def get_tracked_python_files():
    import git
    repo = git.Repo(".")
    tracked_files = repo.git.ls_files().split("\n")
    tracked_files = [ file for file in tracked_files if file.endswith(".py") ]
    return tracked_files

def get_untracked_python_files():
    import git
    repo = git.Repo(".")
    untracked_files = repo.untracked_files
    untracked_files = [ file for file in untracked_files if file.endswith(".py") ]
    return untracked_files

if __name__ == "__main__":
    with handler():
        main()

