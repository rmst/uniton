
UNITYENGINE_DLL="/Applications/Unity/Hub/Editor/2020.2.1f1/Unity.app/Contents/Managed/UnityEngine.dll"

all:
	csc -target:library -r:${UNITYENGINE_DLL} -r:./lib/AsyncGPUReadbackPlugin.dll -out:./out/pysharp.dll ./src/*.cs