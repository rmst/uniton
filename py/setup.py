from setuptools import setup, find_packages

import sys
if sys.version_info < (3, 6):
  sys.exit('Sorry, Python < 3.6 is not supported')

VERSION = open('VERSION', 'r').read()

setup(
    name='uniton',
    version=VERSION,
    description='Control Unity from Python',
    url='https://github.com/rmst/uniton',
    author='Simon Ramstedt',
    author_email='simonramstedt@gmail.com',
    license='',
    packages=find_packages(),
    scripts=[],
    install_requires=[
        
    ],
    zip_safe=False,
    include_package_data=True
)