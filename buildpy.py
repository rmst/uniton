# The following variables should be set
#	export TWINE_USERNAME='...'
#	export TWINE_PASSPORT='...'
from contextlib import contextmanager
from xbrain import xb

from os.path import dirname, join
import protocol
import buildcs

CS = join(dirname(__file__), 'cs')
PY = join(dirname(__file__), 'py')


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


def dev():
  open(f"{PY}/uniton/core.dll", 'wb').write(buildcs.core_dll())
  open(f"{PY}/uniton/protocol.py", "w").write(protocol.template_py())


def pypi():
  open(f"{PY}/uniton/core.dll", 'wb').write(buildcs.core_dll())
  open(f"{PY}/uniton/protocol.py", "w").write(protocol.template_py())

  with cwd(PY):
    s('pip install twine')
    s('rm -rf build dist')
    s('python setup.py sdist bdist_wheel')
    s(f'TWINE_USERNAME={xb.twine.u} TWINE_PASSPORT={xb.twine.pw} twine upload dist/*')
    s('rm -rf dist build')


if __name__ == '__main__':
  pypi()

