# Uniton

Uniton is a framework the Unity game engine from Python.

### Install
Uniton can be used with any Unity project. Just drop [uniton.dll](https://github.com/rmst/uniton/raw/main/uniton.dll) somewhere into the project's `Assets` directory.

Install the Python package via
```bash
pip install uniton
```

### Usage
To connect to a running Unity process do
```python
from uniton import Uniton
ps = Uniton()
```

