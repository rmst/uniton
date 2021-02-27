from setuptools import setup, find_packages

import sys
if sys.version_info < (3, 6):
  sys.exit('Sorry, Python < 3.6 is not supported')

setup(
    name='uniton',
    version='0.1.0',
    description='Async RPC connecting Python to C# and Unity3D',
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