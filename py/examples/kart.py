
from uniton import Cs

cs = Cs()

# cs object acts as the C# root namespace
# to print a message we can therefore do
# cs.Un.. (yes autocomplete works in the REPL)
cs.UnityEngine.Debug.Log("Hello World!")

# timer is running out
# let's try if we can do sth about that
gm = cs.UnityEngine.GameObject.Find("GameManager")
tm = gm.GetComponent("TimeManager")
tm.TotalTime  # returns remaining time
tm.TotalTime = 100
tm.StopRace()  # timer will stop

# okay, let's try to make something move
kart = cs.ue.GameObject.Find("KartClassic_Player")
kart = kart.GetComponent("ArcadeKart")

kart.Rigidbody.velocity  # ok but what type is that?
kart.Rigidbody.velocity.GetType()  # UnityEngine.Vector3

kart.Rigidbody.velocity = cs.ue.Vector3(30, 0, 0)  # goes backwards
kart.Rigidbody.velocity = cs.ue.Vector3(-30, 0, 0)

# Cool this is cute, but let's shift gears
