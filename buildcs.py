
from os import system as s
from os.path import dirname, join

UNITYENGINE_DLL = "/Applications/Unity/Hub/Editor/2020.2.1f1/Unity.app/Contents/Managed/UnityEngine.dll"
UNITYEDITOR_DLL = "/Applications/Unity/Hub/Editor/2020.2.1f1/Unity.app/Contents/Managed/UnityEditor.dll"

CS = join(dirname(__file__), 'cs')

r = lambda f: f()


def dllname(flavor):
	return 'uniton.dll' if flavor == 'free' else 'uniton-' + flavor + '.dll'


def dll(flavor='free'):
	s(f"csc -target:library \
		-r:{UNITYENGINE_DLL} \
		-r:{UNITYEDITOR_DLL} \
		-r:{CS}/lib/AsyncGPUReadbackPlugin.dll \
		-out:{CS}/out/{dllname(flavor)} \
		{CS}/src/*.cs \
		{CS}/src/{flavor}/*.cs")


# @r
def dlls():
	dll(flavor='free')
	dll(flavor='plus')
	dll(flavor='pro')


def link_cs(target, flavor='pro'):
	s(f"rm -rf {target}/Uniton; mkdir {target}/Uniton")
	s(f"ln -sf {CS}/src/*.cs {target}/Uniton/")
	s(f"mkdir {target}/Uniton/{flavor}")
	s(f"ln -sf {CS}/src/{flavor}/*.cs {target}/Uniton/{flavor}/")


def link_dll(target, flavor):
	s(f"rm -rf {target}/Uniton && mkdir {target}/Uniton")
	s(f"ln -sf {CS}/out/{dllname(flavor)} {target}/Uniton/")


def test_cs(flavor='pro'):
	dll(flavor)
	link_cs('/Users/simon/dev/UnityKart3/Assets', flavor)
	link_cs('/Users/simon/dev/unpy/unity/Unpy/Assets/Scripts', flavor)
	link_cs('/Users/simon/dev/ue/temple/Assets', flavor)


# @r
def test_dll(flavor='pro'):
	dll(flavor)
	link_dll('/Users/simon/dev/UnityKart3/Assets', flavor)
	link_dll('/Users/simon/dev/unpy/unity/Unpy/Assets/Scripts', flavor)
	link_dll('/Users/simon/dev/ue/temple/Assets', flavor)


def bootstrap_dll():
	s(f"csc -target:library \
		-r:{UNITYENGINE_DLL} \
		-r:{UNITYEDITOR_DLL} \
		-r:{CS}/lib/AsyncGPUReadbackPlugin.dll \
		-out:{CS}/out/bootstrap.dll \
		{CS}/src/bootstrap/*.cs")


# @r
def test_bootstrap_dll():
	bootstrap_dll()
	target = '/Users/simon/dev/unpy/unity/Unpy/Assets/Scripts'
	s(f"rm -rf {target}/Uniton && mkdir {target}/Uniton")
	s(f"ln -sf {CS}/out/bootstrap.dll {target}/Uniton/")


@r
def test_boostrap_cs():
	target = '/Users/simon/dev/unpy/unity/Unpy/Assets/Scripts'
	s(f"rm -rf {target}/Uniton && mkdir {target}/Uniton")
	s(f"ln -sf {CS}/src/bootstrap/bootstrap.cs {target}/Uniton/")



# @r
def example_builds():
	# test_dll('pro')
	# input("Press enter when all examples have finished building!")
	# TODO: automatic unity build
	import shutil
	print("zipping...")
	shutil.make_archive('cs/out/kart_mac', 'zip', '/Users/simon/dev/UnityKart3/Out/Kart.app')
	shutil.make_archive('cs/out/kart_linux', 'zip', '/Users/simon/dev/UnityKart3/Out/Kart-Linux')
	shutil.make_archive('cs/out/kart_windows', 'zip', '/Users/simon/dev/UnityKart3/Out/Kart-Windows')

	shutil.make_archive('cs/out/temple_mac', 'zip', '/Users/simon/dev/ue/temple/Out/Temple.app')
	shutil.make_archive('cs/out/temple_linux', 'zip', '/Users/simon/dev/ue/temple/Out/Temple-Linux')


