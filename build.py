

import os
from inspect import cleandoc
from os.path import dirname, join
from subprocess import check_output
from xbrain import xb
from protocol import UNITON_VERSION
UNITON_PUBLIC = "../uniton"
DLL_NAME = "uniton.dll"
RELEASE_MESSAGE = 'new versioning system'


def s(*args):
  import os
  assert os.system(*args) == 0


def r(f):
  f()


def proto():
  s("python protocol.py py > py/uniton/protocol.py")
  s("python protocol.py cs > cs/src/Protocol.cs")


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
  proto()
  s(f"git add . && git commit -m {RELEASE_MESSAGE!r} && git push")
  s(f"git tag -a v{UNITON_VERSION} -m '{RELEASE_MESSAGE!r}'")
  s(f"git push --follow-tags")




def cs_release():
  import buildcs
  buildcs.dlls()
  landing_page()
  landing_page_tag()
  landing_page_asset


def py_release():
  import buildpy
  # TODO: buildpy.

