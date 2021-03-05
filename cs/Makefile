DIR:=$(strip $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST)))))
UNITYENGINE_DLL="/Applications/Unity/Hub/Editor/2020.2.1f1/Unity.app/Contents/Managed/UnityEngine.dll"
#SHELL := /bin/zsh
NAME:=uniton.dll

all:
	csc -target:library \
		-r:${UNITYENGINE_DLL} \
		-r:./lib/AsyncGPUReadbackPlugin.dll \
		-out:./out/${NAME} \
		./src/*.cs

test:
	ln -sf ${DIR}/src/* /Users/simon/dev/unpy/unity/Unpy/Assets/Scripts/
	ln -sf ${DIR}/src/* /Users/simon/dev/UnityKart3/Assets/