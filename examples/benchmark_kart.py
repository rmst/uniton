import uniton
# import numpy as np
# import imageio
# from timeit import timeit

ue = uniton.UnityEngine()
ue.pause()

ue.Uniton.Log.level = 3  # suppress log messages


gm = ue.GameObject.Find("GameManager")  # otherwise we run out of time
tm = gm.GetComponent("TimeManager")
tm.TotalTime = 10000
tm.StopRace()

cam = ue.GameObject.Find("Main Camera").GetComponent("Camera")

cam.set_enabled(False)
print("Cameras disabled")

w, h = 256, 128
tex = ue.RenderTexture.GetTemporary(w, h, 0, ue.RenderTextureFormat.ARGB32)


cam.targetTexture = tex

render = ue.Uniton.RenderTools.RenderAsync
readback = ue.Uniton.RenderTools.PollReadbackRequest

# tex_raw = tex.GetRawTextureData

req = render(cam)
# [c.u.step() for _ in range(20)]

res = readback(req).py()
# c.u.step()


import numpy as np
img = np.frombuffer(res, dtype=np.uint8).reshape(h, w, 4)
# imageio.imsave("/home/simon/test.png", img[::-1])  # flip image horizontally and save


ue.Time.fixedDeltaTime = 0.02  # the default
ue.Time.captureDeltaTime = 0.02  # aligns Update calls with FixedUpdate calls

print(f"{ue.SystemInfo.supportsAsyncGPUReadback = }")

kart = ue.GameObject.Find("KartClassic_Player")
kart = kart.GetComponent("ArcadeKart")

from collections import deque

def test(n):
  req = None
  for _ in range(n):
    req = render(cam)
    [ue.step() for _ in range(1)]
    # c.u.obj_id_gen.py()

    kart.Rigidbody.velocity = ue.Vector3(-30, 0, 0)

    res = readback(req).py
    img = np.frombuffer(res.wait(), dtype=np.uint8).reshape(h, w, 4)


print("start timing...")
from timeit import timeit
n = 3000
t = timeit(lambda: test(n), number=1)

frames_per_step = ue.Time.captureFramerate.py() * ue.Time.fixedDeltaTime.py()
print("frames per step", frames_per_step)
frames = n
print(f"rendered {frames} frames at {frames/t} fps")


from IPython import embed

embed()
