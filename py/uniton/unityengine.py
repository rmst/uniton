
from functools import lru_cache
from .unityproc import UnityProc

"""
IMPORTANT NOTE ON TIMING IN THE UNITY ENGINE - FIXEDUPDATE VS UPDATE

This is assuming you already know when `Update` and `FixedUpdate` are called. If you don't, check this https://answers.unity.com/questions/640828/can-anyone-link-to-explain-unitys-game-loop.html.

Here, we're talking about timing when we're in "capture mode", i.e. when `Time.captureDeltaTime = 1 / Time.captureFramerate != 0`. In that case real time doesn't matter. Instead, `FixedUpdate` and `Update` will run at a constant fraction of each other. The tricky part is to understand what that rate is. Normally, you'd think the following holds

```FixedUpdates = Time.fixedDeltaTime / Time.captureDeltaTime * Updates```

However, if `Time.timeScale != 1`, then `Time.fixedDeltaTime` is enforced in scaled time (i.e. `Time.time`) and `Time.captureDeltaTime` is enforced in unscaled time (i.e. `Time.time / Time.timeScale`). Therefore, we need

```Time.captureDeltaTime  = actualCaptureDeltaTime / Time.timeScale```

or alternatively

```Time.captureFrameRate = actualCaptureFramerate * Time.timeScale```

It seems silly but maybe the Unity devs had their reasons. 

Note that generally `Time.timeScale` should be set to `100` to allow the engine to run faster than real-time. Careful, though, if you set it to higher than `100` Unity will silently reject the change!
"""


# noinspection PyProtectedMember
class UnityEngine(UnityProc):
  _default_settings = (1., 0.02, 0., 1)  # the real values will be set on stepping=True

  # def __init__(self, ue):
  #   super().__init__(ue, "UnityEngine")

  def pause(self):
    self._default_settings = (
      self.Time.timeScale,
      self.Time.fixedDeltaTime,
      self.Time.captureDeltaTime,
      self.QualitySettings.vSyncCount,
    )
    self.Time.timeScale = 100  # Warning: 100 is the max value. if higher Unity will silently reject the change!
    self.QualitySettings.vSyncCount = 0  # otherwise Update can be artificially slowed down to match the display refresh rate
    self.time._update_engine_timing()

    self._backend.setStepping(True)

  def paused(self):
    return self._backend.stepping.py()

  def resume(self):
    (
      self.Time.timeScale,
      self.Time.fixedDeltaTime,
      self.Time.captureDeltaTime,
      self.QualitySettings.vSyncCount,
    ) = self._default_settings

    self._backend.setStepping(False)

  def step(self):
    if "_step" not in vars(self):
      self._step = self._backend.step
    self._step()

  @property
  @lru_cache(maxsize=None)
  def time(self):
    from .timing import Time
    return Time(self)

  @property  # don't cache as the active scene could change!
  def scene(self):
    from .scene import Scene
    active_scene = self.SceneManagement.SceneManager.GetActiveScene()
    return Scene(active_scene)

  def reset(self):
    self.Application.LoadLevel(0)
