
from distutils.core import setup
setup(name='common',
      version='1.0',
      py_modules=['common', 'db', 'print'],
      install_requires = [
          'colorama==0.3.9',
          'Columnar==1.3.1',
          'aiohttp==3.7.3',
          'requests==2.25.1',
          'timeago==1.0.14',
          'python_dateutil==2.8.2'
      ]
)

