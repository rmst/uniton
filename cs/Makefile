DIR:=$(strip $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST)))))
UNITYENGINE_DLL="/Applications/Unity/Hub/Editor/2020.2.6f1/Unity.app/Contents/Managed/UnityEngine.dll"
UNITYEDITOR_DLL="/Applications/Unity/Hub/Editor/2020.2.6f1/Unity.app/Contents/Managed/UnityEditor.dll"
FLAVOR:=plus

dll:
	csc -target:library \
		-r:${UNITYENGINE_DLL} \
		-r:${UNITYEDITOR_DLL} \
		-r:./lib/AsyncGPUReadbackPlugin.dll \
		-out:./out/${NAME} \
		./src/*.cs \
		./src/${FLAVOR}/*.cs
dlls:
	make dll FLAVOR=free NAME=uniton.dll
	make dll FLAVOR=plus NAME=uniton-plus.dll
	make dll FLAVOR=pro NAME=uniton-pro.dll

src-link:
	rm -rf ${TGT}/Uniton; mkdir ${TGT}/Uniton
	ln -sf ${DIR}/src/*.cs ${TGT}/Uniton/
	mkdir ${TGT}/Uniton/${FLAVOR}
	ln -sf ${DIR}/src/${FLAVOR}/*.cs ${TGT}/Uniton/${FLAVOR}/

#test:
#	ln -sf ${DIR}/src/* /Users/simon/dev/unpy/unity/Unpy/Assets/Scripts/
#	ln -sf ${DIR}/src/* /Users/simon/dev/UnityKart3/Assets/
#	ln -sf ${DIR}/src/* /Users/simon/dev/ue/temple/Assets/
src-test:
	make src-link TGT=/Users/simon/dev/UnityKart3/Assets/ FLAVOR=pro


dll-link:
	rm -rf ${TGT}/Uniton; mkdir ${TGT}/Uniton
	ln -sf ${DIR}/out/${NAME} ${TGT}/Uniton/

dll-test:
	make dll FLAVOR=free NAME=uniton.dll
	make dll-link TGT=/Users/simon/dev/UnityKart3/Assets/ NAME=uniton.dll
	#make dll-link_cs TGT=/Users/simon/dev/UnityKart3/Assets/