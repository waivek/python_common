
# https://www.python.org/dev/peps/pep-0508/#environment-markers
from setuptools import setup
import sys
# check if module rich is installed

# import rich
import pip._vendor.rich as rich

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


print(f"{sys.argv = }")

if len(sys.argv) >=3 and sys.argv[1] == 'sdist' and sys.argv[2] == 'bdist_wheel':
    remove_dist_directory()
    new_version = get_new_version()
else:
    usage_message = r"""
    [red]Usage:[/red] 

        [bold]python setup.py sdist bdist_wheel[/bold]
    
    If twine is not installed, install it using:

        [bold]pip install twine[/bold]

    Then upload the package to PyPI using:

        [bold]twine upload dist/*[/bold]

    If you get asked for a username and password, you need to have ~/.pypirc file with the following content:

        \[distutils]
        index-servers =
            pypi

        \[pypi]
        repository: https://upload.pypi.org/legacy/
        username: waivek 
        password: <your password>
    """
    rich.print(usage_message)
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

