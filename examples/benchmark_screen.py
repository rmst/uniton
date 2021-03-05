import numpy as np
import imageio
from timeit import timeit
from uniton import UnityEngine
from uniton.render import QueuedRenderer

ue = UnityEngine("/Users/simon/dev/UnityKart3/Kart.app/Contents/MacOS/New Unity Project")
# ue = uniton.UnityEngine()

ue.pause()
# ue.Uniton.Log.level = 3  # suppress log messages


ue.scene.BackgroundMusic.SetActive(False)  # not necessary but nice

cam = ue.scene.Main_Camera.Camera

# we need to make sure that nothing is rendering to the screen because that can slow us down by 10x
cam.enabled = False  # this is the only camera in the scene
ue.scene.GameManager.SetActive(False)  # disables all GUI in the Kart game


def test(n):
  # w, h = 1024, 768
  w, h = 512, 256
  # w, h = 256, 64
  renderer = QueuedRenderer(cam, w, h)

  videowriter = imageio.get_writer('test.mp4', fps=25)
  kart = ue.scene.KartClassic_Player.Rigidbody  # we want to make things move

  for _ in range(n):
    frame = renderer.render()
    kart.velocity = ue.Vector3(0, 0.5, 0)
    kart.angularVelocity = ue.Vector3(0, 1., 0)
    ue.step()
    videowriter.append_data(frame)

  videowriter.close()


print("start timing...")
from timeit import timeit
n = 1000
t = timeit(lambda: test(n), number=1)

print(f"Rendered {n} frames and simulated {0.04 * n} seconds of game time in {t} seconds.")
print(f"On average, that is {n/t} frames and simulated {0.04 * n / t} seconds of game time per second.")

from IPython import embed; embed()
