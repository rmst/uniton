# Uniton

Uniton is a framework to control the Unity game engine from Python.

[![Uniton Demo Video](./res/yt_thumbnail.png)](https://www.youtube.com/watch?v=FIpt2yv623k)



### Features
- [x] naturally interact with all C# objects, functions, classes
- [x] full autocomplete and inspection for all C# objects (live coding)
- [x] fast, asynchronous execution
- [x] precise control over game time
- [x] faster-than-real-time rendering and simulation


### Install
Uniton can be used with any Unity project. Just drop the [uniton.dll](https://github.com/rmst/uniton/raw/main/uniton.dll) somewhere into the project's `Assets` directory.

Install the Python package via
```bash
pip install uniton
```

### Usage
To connect to a running Unity process do

```python
from uniton import UnityEngine
ue = UnityEngine()
```

Control time via
```python
ue.pause()
ue.step()  # advances game time by ue.time.delta and renders one frame (if scene has enabled cameras)
ue.resume()
```

Access game objects via
```python
ue.scene.<gameobject>.<child_gameobject>

# Access components within game objects via
ue.scene.<gameobject>.<component>
```

Access any C# class via
```python
ue.<namespace>.<classname>

# The 'UnityEngine' root namespace can be omitted, i.e.
ue.<classname> == ue.UnityEngine.<classname>

# instantiate any class via a call, e.g.
v = ue.Vector3(0, 1, 0)
```

Access values from C#/Unity
```python
v.x  # 'x' representation of the property of a C# Vector3 object
v.x.py # immediately returns a promise and triggers 'v.x' to be sent back asynchronously
v.x.py() # blocks until the value has been received and returns the value

# Currently, only a few types can be received, e.g. int, float, str, byte arrays.
```


### License
This is a free-to-use alpha version. I will probably put the Python part of this framework under the GPLv2. I'd be happy and thankful for contributions. Even though I might put a "pro" version of this in the Unity Asset Store at some point, there will always be a free-to-use version.

