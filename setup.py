
# https://www.python.org/dev/peps/pep-0508/#environment-markers
from setuptools import setup
import sys
import importlib.util
# check if module rich is installed

# import rich
import pip._vendor.rich as rich

def get_new_version():
    import urllib.request
    from urllib.error import URLError
    import json
    package_name = "waivek"
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        req = urllib.request.urlopen(url)
    # except urllib.request.URL
    # catch URLError
    except URLError as e:
        error = e
        print(f"Error: {error}")
        print(f"Could not fetch {url}")
        sys.exit(1)

    D = json.load(req)
    version = D["info"]["version"]
    major, minor, patch = version.split(".")
    patch = int(patch) + 1
    new_version = f"{major}.{minor}.{patch}"
    print(f"{package_name} version: {version} -> {new_version}")
    return new_version

def remove_dist_directory():
    import shutil
    shutil.rmtree("dist", ignore_errors=True)

def get_usage():
    if len(sys.argv) >= 3 and sys.argv[1] in ['egg_info', 'install', 'clean']:
        # `pip install .` -> ['/home/vivek/python_common/setup.py', 'egg_info', '--egg-base', '/tmp/pip-pip-egg-info-knsmhso3']
        return "PIP_INSTALL_DOT"
    # ['/home/vivek/python_common/setup.py', 'bdist_wheel', '-d', '/tmp/pip-wheel-4pt1wlji']
    if len(sys.argv) >= 3 and sys.argv[1] == 'bdist_wheel' and sys.argv[2] == '-d':
        return "PIP_INSTALL_DOT"
    if len(sys.argv) >= 3 and sys.argv[1] == 'sdist' and sys.argv[2] == 'bdist_wheel':
        return "UPLOAD_TO_PYPI"
    return "UNKNOWN"

temp_usage = get_usage()
if temp_usage == "UNKNOWN":
    usage_message = r"""
    Passd args: {0}

    [red]Usage:[/red] 

        [bold]python setup.py sdist bdist_wheel[/bold]

    Then upload the package to PyPI using:

        [bold]twine upload dist/*[/bold]

    If you get asked for a username and password, you need to have [bold]~/.pypirc[/bold] file with the following content:

        \[pypi]
        username: __token__ 
        password: <your api token, with `pypi` prefix>
    """.format(sys.argv)
    rich.print(usage_message)
    sys.exit(1)

usage = get_usage()

if usage == "UPLOAD_TO_PYPI":
    missing_modules = False
    if importlib.util.find_spec("twine") is None:
        rich.print("Please install twine using [bold]pip install twine[/bold]")
        missing_modules = True
    if importlib.util.find_spec("wheel") is None:
        rich.print("Please install wheel using [bold]pip install wheel[/bold]")
        missing_modules = True
    if missing_modules:
        sys.exit(1)

if usage == "UPLOAD_TO_PYPI":
    remove_dist_directory()

new_version = "0.0.0" 
if usage == "UPLOAD_TO_PYPI":
    new_version = get_new_version()
py_modules = ['color', 'common', 'data', 'db', 'error', 'frame', 'get', 'ic', 'print_utils', 'reltools', 'timer', 'trace']
py_modules = ['waivek.' + x for x in py_modules]
long_description = open('README.md').read()
setup(
        name='waivek',
        version=new_version,
        packages=['waivek'],
        py_modules = py_modules,
        install_requires = [
            'aiohttp>=3.8.1',
            'executing==0.8.2',
            'python_dateutil==2.8.2',
            'loguru',# for `log.py`
            'timeago==1.0.14',
            'columnar==1.3.1',
            'pysqlite3-binary; platform_system=="Linux"'
        ],
        long_description=long_description,
        long_description_content_type='text/markdown'
)

