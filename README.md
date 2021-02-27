# Uniton

Uniton is a framework for controlling C# programs and the Unity game engine from Python.

### Install
To use Uniton in a new Unity3D project just drop [uniton.dll](https://github.com/rmst/uniton/raw/main/uniton.dll) somewhere into the project's `Assets` directory.

Install the Python package via
```bash
pip install uniton
```

### Usage
To connect to a running Unity process run
```python
from uniton import Unity
u = Unity()
```

Time can be controlled via
```
cs.unity.pause()
cs.unity.resume()
cs.unity.step()
```