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
_.TotalTime  # returns remaining time
__.TotalTime = 10000
# alright, we're safe
# ---

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
