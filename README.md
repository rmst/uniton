# Pysharp
Pysharp is a framework for controlling C# programs and the Unity game engine from Python.

### Install
To use Pysharp in a new Unity3D project just drop [pysharp.dll](https://github.com/rmst/pysharp/raw/main/pysharp.dll) somewhere into the project's `Assets` directory.

Install the Python package via
```bash
pip install pysharp
```

### Usage
To connect to a running C# process do
```python
from pysharp import Pysharp
ps = Pysharp()
```

