DIR:=$(strip $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST)))))
UNITYENGINE_DLL?=$(error UNITYENGINE_DLL is not set)
UNITYEDITOR_DLL?=$(error UNITYEDITOR_DLL is not set)
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

src-test:
	@echo "Set UNITY_PROJECT_PATH environment variable to test"
	@test -n "$$UNITY_PROJECT_PATH" && make src-link TGT=$$UNITY_PROJECT_PATH/Assets/ FLAVOR=pro || true


dll-link:
	rm -rf ${TGT}/Uniton; mkdir ${TGT}/Uniton
	ln -sf ${DIR}/out/${NAME} ${TGT}/Uniton/

dll-test:
	@echo "Set UNITY_PROJECT_PATH environment variable to test"
	make dll FLAVOR=free NAME=uniton.dll
	@test -n "$$UNITY_PROJECT_PATH" && make dll-link TGT=$$UNITY_PROJECT_PATH/Assets/ NAME=uniton.dll || true