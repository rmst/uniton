import uniton
# import numpy as np
# import imageio
# from timeit import timeit
from uniton.render import QueuedRenderer

import os
ue = uniton.UnityEngine(os.getenv("UNITY_BUILD_PATH"))
# u = uniton.Unity()
ue.pause()

# u.Uniton.Log.level = 3  # suppress log messages

cam = ue.GameObject.Find("Main Camera").GetComponent("Camera")

cam.set_enabled(False)
print("Cameras disabled")

w, h = 256, 128


print(f"{ue.SystemInfo.supportsAsyncGPUReadback = }")
print(f"{ue.QualitySettings.maxQueuedFrames = }")
print(f"{ue.QualitySettings.vSyncCount = }")
print(f"{ue.Application.targetFrameRate = }")


def test_queue(n):
  import imageio
  import numpy as np
  cam.usePhysicalProperties = True  # necessary to use cam.focalLength

  videowriter = imageio.get_writer('test.mp4', fps=ue.Time.captureFramerate.py())

  qr = QueuedRenderer(cam, w, h, 4, 3)
  for i in range(n):
    cam.focalLength = i  # to see that something is happening
    ue.step()  # trigger FixedUpdate and Update
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
