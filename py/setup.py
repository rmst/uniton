from setuptools import setup, find_packages
from os.path import dirname, join

import sys
if sys.version_info < (3, 6):
  sys.exit('Sorry, Python < 3.6 is not supported')


def direct_import(path, name=None):
    import importlib.util
    from os.path import basename, splitext
    if not name:
        name = splitext(basename(path))[0]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

protocol = direct_import(join(dirname(__file__), "uniton", "protocol.py"))

setup(
    name='uniton',
    version=protocol.UNITON_VERSION,
    description='Control Unity from Python',
    url='https://github.com/rmst/uniton',
    author='Simon Ramstedt',
    author_email='simonramstedt@gmail.com',
    license='',
    packages=find_packages(),
    scripts=[],
    install_requires=[
        # there shouldn't be any hard dependecies (we promise that in the readme)
    ],
    zip_safe=False,
    include_package_data=True
)