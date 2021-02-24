import unpy
import numpy as np
import imageio
from timeit import timeit

import unpy.connection

c = unpy.connection.Connection()
# c.u.SetDebug(True)

c.u.setStepping(True)
print("Stepping enabled at step", c.u.fixed_updates)

[c.cs.QualitySettings.DecreaseLevel() for i in range(10)]
# [c.cs.QualitySettings.IncreaseLevel() for i in range(10)]
print("Quality level ", c.cs.QualitySettings.GetQualityLevel())

c.cs.Time.timeScale = 100
c.cs.Time.fixedDeltaTime = 0.01 # default = 0.0167
print("Set timescale to ", c.cs.Time.timeScale, " and fixedDeltaTime to ", c.cs.Time.fixedDeltaTime)
c.cs.Time.captureFramerate = 1000

w, h = 128, 64
cam = c.cs.GameObject.Find("Camera").GetComponent("Camera")
# go = c.cs.GameObject("abc")
go = c.cs.GameObject.Find("screen")
go.AddComponent(c.cs.Camera)
cam2 = go.GetComponent("Camera")

cam.set_enabled(False)
cam2.set_enabled(False)
print("Cameras disabled")

tex = c.cs.Texture2D(w, h, c.cs.TextureFormat.RGB24, False, False)
# c.cs.RenderTools.RenderToTexture(cam, tex, c.cs.Rect(0.3, 0.3, 0.01, 0.01))
rect = c.cs.Rect(0., 0., 1., 1.)
rtt2 = c.cs.RenderTools.RenderToTexture2
rtt = c.cs.RenderTools.RenderToTexture

tex_raw = tex.GetRawTextureData
def render():
    c.u.step()
    rtt(cam2, tex, rect)
    # rtt2(cam, cam2, tex)
    # data = c.u.best(3).to_py()
    data = tex_raw().to_py()

    # c.u.step()
    return data

def rall(n):
    d = [render() for i in range(n)]
    [e.wait() for e in d]

def rall_block(n):
    d = [render().wait() for i in range(n)]

def rall_delay(n, d):
    p = []
    for i in range(n):
        p.append(render())
        if i >= d:
            p[i-d].wait()
def t1(n=100):
    print(timeit(lambda: rall(n), number=1))

def t2(n=100):
    print(timeit(lambda: rall_block(n), number=1))

def t3(n=100, d=1):
    print(timeit(lambda: rall_delay(n, d), number=1))

t2()

b = np.frombuffer(render().wait(), dtype=np.uint8).reshape(h, w, 3)

imageio.imsave("test3.png", b[::-1])  # flip image horizontally and save

# import pdb; pdb.set_trace()
# import code; code.interact(local=locals())
from IPython import embed; embed();