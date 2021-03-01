# Uniton C# Backend

C# code for the Uniton backend. Everything is compiled into `uniton.dll`. To use Uniton in a new Unity3D project just drop the `uniton.dll` somewhere into the project's `Assets` directory.


### Build
To compile all the `.cs` files into `out/uniton.dll` the [Mono C# compiler](https://www.mono-project.com/download/stable/) `csc` is needed. To compile run

```bash
make  # check Makefile
cp out/uniton.dll ~/dev/uniton/
```



### Development
To put `/src` directly into a Unity project the files can be symlinked via
```bash
ln -sf $(pwd)/src/* destination
```
E.g.
```
ln -sf $(pwd)/src/* /Users/simon/dev/unpy/unity/Unpy/Assets/Scripts/
```


### Demo
This is a quick demo of Uniton. Uniton is a framework for controlling C# programs and the Unity game engine from Python.

To show you how easy it to use Uniton, I'm going to open up this example project that comes with Unity.
