# Pysharp C# Backend

C# code for the Pysharp backend. Everything is compiled into `pysharp.dll`. To use Pysharp in a new Unity3D project just drop the `pysharp.dll` somewhere into the project's `Assets` directory.


### Build
To compile all the `.cs` files into `out/pysharp.dll` the [Mono C# compiler](https://www.mono-project.com/download/stable/) `csc` is needed. To compile run

```bash
make  # check Makefile
cp out/pysharp.dll ~/dev/pysharp/
```



### Development
To put `/src` directly into a Unity project the files can be symlinked via
```bash
ln -sf $(pwd)/src/* destination
```



### Demo
This is a quick demo of Pysharp. Pysharp is a framework for controlling C# programs and the Unity game engine from Python.

To show you how easy it to use Pysharp, I'm going to open up this example project that comes with Unity.

