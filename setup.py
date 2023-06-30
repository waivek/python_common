# https://www.python.org/dev/peps/pep-0508/#environment-markers
from setuptools import setup
import sys
def get_new_version():
    import urllib.request
    import json
    package_name = "waivek"
    url = f"https://pypi.org/pypi/{package_name}/json"
    req = urllib.request.urlopen(url)
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

if len(sys.argv) >=3 and sys.argv[1] == 'sdist' and sys.argv[2] == 'bdist_wheel':
    remove_dist_directory()
    new_version = get_new_version()
else:
    print("Usage: python setup.py sdist bdist_wheel")
    sys.exit(1)

py_modules = ['color', 'common', 'data', 'db', 'error', 'frame', 'get', 'ic', 'print_utils', 'reltools', 'timer', 'trace']
py_modules = ['waivek.' + x for x in py_modules]
long_description = open('README.md').read()
setup(
        name='waivek',
        version=new_version,
        packages=['waivek'],
        py_modules = py_modules,
        install_requires = [
            'aiohttp==3.8.1',
            'executing==0.8.2',
            'python_dateutil==2.8.2',
            'timeago==1.0.14',
            'pysqlite3-binary; platform_system=="Linux"'
        ],
        long_description=long_description,
        long_description_content_type='text/markdown'
)

