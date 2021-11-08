# this is meant to be run interactively in ipython

# This is short intro to Uniton. Uniton let's you control Unity from Python. You can use it with any Unity project. We're going use this Kart project that comes with Unity.
from uniton import UnityEngine

ue = UnityEngine()

# Among other things the `ue` object acts as the C# root namespace
# ue.<Tab> autocomplete works in the REPL for all namespaces, types and objects

# To print a message we can do
ue.UnityEngine.Debug.Log("Hello World!")

# The namespaces are organized in a strict hierarchy. The only exception is the "UnityEngine" namespace which is directly available from `ue`.

# Therefore we can also do
ue.Debug.Log("Hello World!")
# ---

# timer is running out
# let's try if we can do sth about that
ue.GameObject.Find("GameManager")
_.GetComponent("TimeManager")
_.TimeRemaining  # returns remaining time
__.TimeRemaining = 10000
# alright, we're safe
# ---

# ue.GameObject.Find("GameManager").GetComponent("TimeManager").TimeRemaining = 10000
# ue.GameObject.Find("Main Camera").GetComponent("Camera").enabled = False


# okay, let's try to make something move
ue.GameObject.Find("KartClassic_Player")
_.GetComponent("ArcadeKart")

# let's give this a name
kart = _
kart.Rigidbody.velocity  # ok but what type is that?
kart.Rigidbody.velocity.GetType()  # UnityEngine.Vector3

kart.Rigidbody.velocity = ue.Vector3(30, 0, 0)  # goes backwards
kart.Rigidbody.velocity = ue.Vector3(-30, 0, 0)

# Cool this is cute, but let's shift gears


# == Rotate ==
kart = ue.scene.KartClassic_Player.Rigidbody  # we want to make things move
for i in range(250):
  kart.velocity = ue.Vector3(0, 0.5, 0)
  kart.angularVelocity = ue.Vector3(0, 1., 0)
  ue.step()


# == Rotate and Render ==
from uniton import UnityEngine
import os
ue = UnityEngine(os.getenv("UNITY_BUILD_PATH"))
ue.pause()

# QueuedRenderer helps with getting frames from Unity without blocking execution
from uniton.render import QueuedRenderer
renderer = QueuedRenderer(camera=ue.scene.Main_Camera.Camera, width=512, height=256)

# create videowriter to encode mp4
import imageio  # install with: pip install imageio imageio-ffmpeg
videowriter = imageio.get_writer('test.mp4', fps=25)

# similar loop as before just now with the renderer and videowriter
kart = ue.scene.KartClassic_Player.Rigidbody

for i in range(250):
  kart.velocity = ue.Vector3(0, 0.5, 0)
  kart.angularVelocity = ue.Vector3(0, 1., 0)
  ue.step()
  frame = renderer.render()
  videowriter.append_data(frame)

videowriter.close()

# We can speed this up by making sure that nothing renders to the screen.
ue.scene.Main_Camera.Camera.enabled = False  # this is the only camera in the scene
ue.scene.GameManager.SetActive(False)  # disables all GUI in the Kart game

# run the above loop againg (will be 10x faster)


# == Fly Trajectory ==
# for some reason, when rendered off-screen, the camera will separate from the kart
import numpy as np
kart = ue.scene.KartClassic_Player.transform
p0 = kart.position
r0 = kart.rotation
for i in range(250):
  progress = i / 250
  kart.position = p0 + ue.Vector3(0, progress**4 * 30, progress * 100)  # 30m up and 100m forwards
  kart.rotation = r0
  ue.step()