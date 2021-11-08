# The following variables should be set
#	export TWINE_USERNAME='...'
#	export TWINE_PASSWORD='...'
from contextlib import contextmanager

from os.path import dirname, join
import os
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
    twine_username = os.getenv("TWINE_USERNAME")
    twine_password = os.getenv("TWINE_PASSWORD")
    s(f'TWINE_USERNAME={twine_username} TWINE_PASSWORD={twine_password} twine upload dist/*')
    s('rm -rf dist build')


if __name__ == '__main__':
  pypi()

