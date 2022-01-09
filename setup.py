# https://www.python.org/dev/peps/pep-0508/#environment-markers
# install_requires = [
#   'python_dateutil==2.8.2',
#   'timeago;platform_system=="Windows"',
#   'colorama;platform_system=="Linux"'
# ]
from distutils.core import setup
setup(name='common',
      version='1.0',
      py_modules=['common', 'db', 'print', 'ic'],
      install_requires = [
          'colorama==0.3.9',
          'Columnar==1.3.1',
          'aiohttp==3.7.3',
          'requests==2.25.1',
          'timeago==1.0.14',
          'python_dateutil==2.8.2',
          'pysqlite3-binary;platform_system=="Linux"'
      ]
)

