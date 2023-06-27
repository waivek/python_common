# https://www.python.org/dev/peps/pep-0508/#environment-markers
from setuptools import setup
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

py_modules = ['color', 'common', 'db', 'error', 'frame', 'get', 'ic', 'print_utils', 'reltools', 'timer', 'trace']
py_modules = ['waivek.' + x for x in py_modules]
long_description = open('README.md').read()
setup(
        name='waivek',
        version='0.1.4',
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

