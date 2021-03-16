# The following variables should be set
#	export TWINE_USERNAME='...'
#	export TWINE_PASSPORT='...'
from contextlib import contextmanager
from xbrain import xb


def s(*args):
  import os
  assert os.system(*args) == 0


def r(f):
  f()


@contextmanager
def cwd(path):
  import os
  orig = os.getcwd()
  os.chdir(path)
  yield
  os.chdir(orig)


@r
def pypi():
  with cwd("py"):
    s('pip install twine')
    s('python setup.py sdist bdist_wheel')
    s(f'TWINE_USERNAME={xb.twine.u} TWINE_PASSPORT={xb.twine.pw} twine upload dist/*')
    s('rm -rf dist build')