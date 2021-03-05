# Uniton

Uniton is a framework to control the Unity game engine from Python. Here is a three-minute intro video:

[![Uniton Demo Video](./res/yt_thumbnail.png)](https://www.youtube.com/watch?v=FIpt2yv623k)



### Features
- [x] naturally interact with all C# objects, functions, classes
- [x] full autocomplete and inspection for all C# objects (live coding)
- [x] fast, asynchronous execution
- [x] precise control over game time
- [x] faster-than-real-time rendering and simulation


### Install
In any Unity project, drop the [uniton.dll](https://github.com/rmst/uniton/raw/main/uniton.dll) into the project's `Assets` directory.

Install the Python package via `pip install uniton`.


### Usage
To connect to a running Unity process do

```python
from uniton import UnityEngine
ue = UnityEngine()  # also accepts a file path to a Unity game and 'host' and 'port' arguments
```

#### Control time via
```python
ue.pause()  # note that this can block the whole Unity Editor
ue.step()  # advances game time by ue.time.delta and renders one frame (if scene has enabled cameras)
# more steps, etc..
ue.resume()
```

#### Access game objects via
```python
ue.scene.<gameobject>.<child_gameobject>

# Access components within game objects via
ue.scene.<gameobject>.<component>
```

#### Access any C# class via
```python
ue.<namespace>.<classname>

# The 'UnityEngine' namespace can be omitted, i.e.
ue.<classname> == ue.UnityEngine.<classname>

# instantiate any class via a call, e.g.
v = ue.Vector3(0, 1, 0)
```

#### Receiving values from C#/Unity
```python
v.x  # representation of the 'x' property of a C# Vector3 object
v.x.py # immediately returns a promise object and triggers 'v.x' to be sent to Python asynchronously
v.x.py() # blocks until the value has been received and returns the value

# Currently, only a few types can be received directly, e.g. int, float, str, byte arrays.
```

#### Rendering and receiveing frames
```python
from uniton import QueuedRenderer

renderer = QueuedRenderer(ue.scene.Main_Camera.Camera, width=512, height=256, render_steps=4, ipc_steps=3)
frame = renderer.render()  # will return a Numpy array of shape (256, 512, 3) and dtype 'uint8'
```

Internally, the frame is produced as follows.
```
Unity GPU (render) --render_queue--> Unity CPU --ipc_queue--> Python
```

Therefore, `frame` actually shows the state of the game a number of `renderer.render()`-calls earlier. To be precise, that number is

```python
renderer.delay() == render_steps + ipc_steps - 2
```

Consequently, the following will block and show the current state of the game.
```python
renderer = QueuedRenderer(ue.scene.Main_Camera.Camera, width=512, height=256, render_steps=1, ipc_steps=1)
frame = render.render()
```

## License
This is a free-to-use alpha version. I will probably publish the Python part of this framework here under the GPLv2. I'd be happy and thankful to receive contributions. Even though I might put a "pro" version of this in the Unity Asset Store at some point, there will always be a free-to-use version.

