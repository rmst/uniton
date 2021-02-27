import uniton
# import numpy as np
# import imageio
# from timeit import timeit
from uniton.render import QueuedRenderer

u = uniton.Unity("/Users/simon/dev/unpy/unity/Unpy/testbin.app/Contents/MacOS/Unpy")
# u = uniton.Unity()
u.stepping = True

ue = u.UnityEngine

# u.Pysharp.Log.level = 3  # suppress log messages

cam = ue.GameObject.Find("Main Camera").GetComponent("Camera")

cam.set_enabled(False)
print("Cameras disabled")

w, h = 256, 128
tex = ue.RenderTexture.GetTemporary(w, h, 0, ue.RenderTextureFormat.ARGB32)


cam.targetTexture = tex

render = u.Pysharp.RenderTools.RenderAsync
readback_wait = u.Pysharp.RenderTools.WaitReadbackRequest
readback_poll = u.Pysharp.RenderTools.PollReadbackRequest

# tex_raw = tex.GetRawTextureData

req = render(cam)
# [c.u.step() for _ in range(20)]

res = readback_wait(req).py()
# c.u.step()

# from IPython import embed; embed()


import numpy as np
# img = np.frombuffer(res, dtype=np.uint8).reshape(h, w, 4)
# imageio.imsave("/home/simon/test.png", img[::-1])  # flip image horizontally and save


ue.Time.fixedDeltaTime = 0.02  # the default
ue.Time.captureDeltaTime = 0.02  # aligns Update calls with FixedUpdate calls

print(f"{ue.SystemInfo.supportsAsyncGPUReadback = }")
print(f"{ue.QualitySettings.maxQueuedFrames = }")


def test_queue(n):
  import imageio
  import numpy as np
  cam.usePhysicalProperties = True  # necessary to use cam.focalLength

  videowriter = imageio.get_writer('test.mp4', fps=ue.Time.captureFramerate.py())

  qr = QueuedRenderer(cam, w, h, 4, 3)
  for i in range(n):
    cam.focalLength = i  # to see that something is happening
    u.step()  # trigger FixedUpdate and Update
    frame = qr.render()
    img = np.frombuffer(frame, dtype=np.uint8).reshape(h, w, 4)
    videowriter.append_data(img[::-1, :, :3])

  videowriter.close()


print("start timing...")
from timeit import timeit
n = 3000
t = timeit(lambda: test_queue(n), number=1)

frames_per_step = ue.Time.captureFramerate.py() * ue.Time.fixedDeltaTime.py()
print("frames per step", frames_per_step)
frames = n
print(f"rendered {frames} frames at {frames/t} fps")   # around 2000 fps on Macbook


# from IPython import embed; embed()
