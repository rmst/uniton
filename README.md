# Pysharp

Pysharp is a framework for controlling C# programs and the Unity game engine from Python.

### Install
Pysharp can be used with any Unity project. Just drop [pysharp.dll](https://github.com/rmst/pysharp/raw/main/pysharp.dll) somewhere into the project's `Assets` directory.

Install the Python package via
```bash
pip install pysharp
```

### Usage
To connect to a running Unity process do
```python
from pysharp import Pysharp
ps = Pysharp()
```

