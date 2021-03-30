from os.path import dirname, join

CS = join(dirname(__file__), 'cs')
PY = join(dirname(__file__), 'py')

UNITYENGINE_DLL = "/Applications/Unity/Hub/Editor/2020.2.1f1/Unity.app/Contents/Managed/UnityEngine.dll"
UNITYEDITOR_DLL = "/Applications/Unity/Hub/Editor/2020.2.1f1/Unity.app/Contents/Managed/UnityEditor.dll"

# TODO: check if we still need AsyncGPUReadbackPlugin.dll for linux

import protocol


def s(*args):
  import os
  assert os.system(*args) == 0


# https://docs.microsoft.com/en-us/dotnet/csharp/language-reference/compiler-options/output
def core_dll():
  open(f"{CS}/src/core/_Protocol.cs", "w").write(protocol.template_cs("Uniton"))

  s(f"csc -target:library \
    -r:{UNITYENGINE_DLL} \
		-r:{UNITYEDITOR_DLL} \
		-r:{CS}/lib/AsyncGPUReadbackPlugin.dll \
		-out:{CS}/out/core.dll \
		{CS}/src/core/*.cs")

  dll = open(f"{CS}/out/core.dll", 'rb').read()
  dll = dll[-239:] + dll
  return dll


def uniton_dll():
  # embedding dlls into each other :D

  open(f"{CS}/src/bootstrap/_Protocol.cs", "w").write(protocol.template_cs("Uniton.Bootstrap"))

  s(f"csc -target:library \
		-r:{UNITYENGINE_DLL} \
		-r:{UNITYEDITOR_DLL} \
		-r:System.Net.Http.dll \
		-r:{CS}/lib/AsyncGPUReadbackPlugin.dll \
		-out:{CS}/out/bootstrap.dll \
		{CS}/src/bootstrap/*.cs")

  open(f"{CS}/src/editor/_Protocol.cs", "w").write(protocol.template_cs("Uniton.Editor"))

  s(f"csc -target:library \
		-r:{UNITYENGINE_DLL} \
		-r:{UNITYEDITOR_DLL} \
		-r:System.Net.Http.dll \
		-res:{CS}/out/bootstrap.dll \
		-r:{CS}/lib/AsyncGPUReadbackPlugin.dll \
		-out:{CS}/out/uniton.dll \
		{CS}/src/editor/*.cs \
	")


def link_uniton_dll(target):
  s(f"rm -rf {target}/Uniton && mkdir {target}/Uniton")
  s(f"ln -sf {CS}/out/uniton.dll {target}/Uniton/")


def test_uniton_dll():
  uniton_dll()
  link_uniton_dll('/Users/simon/dev/unpy/unity/Unpy/Assets/Scripts')
  link_uniton_dll('/Users/simon/dev/ue/empty/Assets')
  link_uniton_dll('/Users/simon/dev/ue/floodedgrounds/Assets')
  link_uniton_dll('/Users/simon/dev/ue/forest/Assets')
  link_uniton_dll('/Users/simon/dev/ue/kart/Assets')
  link_uniton_dll('/Users/simon/dev/ue/temple/Assets')
  link_uniton_dll('/Users/simon/dev/ue/windridgecity/Assets')


def link_cs(target):
  s(f"rm -rf {target}/Uniton && mkdir {target}/Uniton")
  s(
    f"mkdir {target}/Uniton/Editor && ln -sf {CS}/src/editor/*.cs {target}/Uniton/Editor")  # contains editor specific stuff
  s(f"mkdir {target}/Uniton/Bootstrap && ln -sf {CS}/src/bootstrap/*.cs {target}/Uniton/Bootstrap")  # standalone
  s(f"mkdir {target}/Uniton/Core && ln -sf {CS}/src/core/*.cs {target}/Uniton/Core")  # core


def test_cs():
  link_cs('/Users/simon/dev/ue/temple/Assets')
  link_cs('/Users/simon/dev/ue/empty/Assets')


def zip_bin(name):
  import shutil
  print(f"zipping {name}")
  shutil.make_archive(f'cs/out/{name}_mac', 'zip', f'/Users/simon/dev/ue/{name}/Out/{name.capitalize()}.app')
  shutil.make_archive(f'cs/out/{name}_linux', 'zip', f'/Users/simon/dev/ue/{name}/Out/{name.capitalize()}-Linux')
  shutil.make_archive(f'cs/out/{name}_windows', 'zip', f'/Users/simon/dev/ue/{name}/Out/{name.capitalize()}-Windows')


def example_builds():
  # test_dll('pro')
  # input("Press enter when all examples have finished building!")
  # TODO: automatic unity build

  # zip_bin('empty')
  # zip_bin('kart')
  # zip_bin('temple')
  # zip_bin('floodedgrounds')
  # zip_bin('windridgecity')
  zip_bin('forest')


if __name__ == '__main__':
  # test_uniton_dll()
  # test_cs()

  example_builds()
