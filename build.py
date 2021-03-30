

import os
from inspect import cleandoc
from os.path import dirname, join
from subprocess import check_output
from xbrain import xb
from protocol import UNITON_VERSION
UNITON_PUBLIC = "../uniton"
DLL_NAME = "uniton.dll"
RELEASE_MESSAGE = 'update examples'
import buildpy
import buildcs

def s(*args):
  import os
  assert os.system(*args) == 0


# def proto():
#   import protocol
#   protocol.py()
#   protocol.cs()


def landing_page():
  # publish landing page to Github
  changelog = cleandoc(f"""
    Uniton Version {UNITON_VERSION} - {RELEASE_MESSAGE}
  """)
  open('public/Changelog', 'w').write(changelog)

  s(f"cp -r public/* {UNITON_PUBLIC}")
  s(f"pushd {UNITON_PUBLIC} && git add . && git commit -m {RELEASE_MESSAGE!r} && git push && popd")
  #pushd cs; NAME={DLL_NAME} make; cp out/{DLL_NAME} {UNITON_PUBLIC}/; popd


def landing_page_tag():
  s(f"pushd {UNITON_PUBLIC} && git tag -a v{UNITON_VERSION} -m {RELEASE_MESSAGE!r} && git push --follow-tags && popd")


def landing_page_asset():
  # TODO: use official gh cli
  # s(f"bash upload-github-release-asset.sh github_api_token={xb.github.uniton.pubtoken} owner=rmst repo=uniton tag=v{UNITON_VERSION} filename=./cs/out/uniton.dll")
  pass


def dev_release():
  # proto()
  s(f"git add . && git commit -m {RELEASE_MESSAGE!r} && git push")
  s(f"git tag -a v{UNITON_VERSION} -m '{RELEASE_MESSAGE!r}'")
  s(f"git push --follow-tags")


# def cs_release():
#   import buildcs, protocol
#   protocol.cs()
#   buildcs.dlls()
#   landing_page()
#   landing_page_tag()
#   landing_page_asset


# def py_release():
#   import buildcs, buildpy, protocol
#   protocol.cs()
#   protocol.py()
#   buildcs.core_dll()
#   buildpy.pypi()


if __name__ == "__main__":
  # buildpy.dev()
  # buildpy.pypi()

  # buildcs.test_uniton_dll()
  # buildcs.test_cs()


  landing_page()
