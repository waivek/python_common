# https://www.python.org/dev/peps/pep-0508/#environment-markers
# install_requires = [
#   'python_dateutil==2.8.2',
#   'timeago;platform_system=="Windows"',
#   'colorama;platform_system=="Linux"'
# ]
from setuptools import setup
setup(
        name='common',
        version='1.0',
        py_modules = ['color', 'common', 'db', 'error', 'frame', 'get', 'ic', 'print_utils', 'reltools', 'timer', 'trace'],
        install_requires = [
            'aiohttp==3.8.1',
            'executing==0.8.2',
            'python_dateutil==2.8.2',
            'timeago==1.0.14',
            'pysqlite3-binary; platform_system=="Linux"'
        ]
)

