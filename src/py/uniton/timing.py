
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



class Time:
  """
  This class only has an effect in 'paused mode'
  """
  def __init__(self, ue):
    self._ue = ue
    self._delta = 0.04
    self._physics_substeps = 2

  @property
  def delta(self):
    return self._delta

  @delta.setter
  def delta(self, v):
    self._delta = v
    if self._ue.paused():
      self._update_engine_timing()

  def _update_engine_timing(self):
    self._ue.Time.captureDeltaTime = self._delta / self._ue.Time.timeScale.py()
    self._ue.Time.fixedDeltaTime = self._desired_fixed_delta()

  def _desired_fixed_delta(self):
    return self._delta / self._physics_substeps

  @property
  def physics_substeps(self):
    return self._physics_substeps

  @physics_substeps.setter
  def physics_substeps(self, v: int):
    self._physics_substeps = v
    if self._desired_fixed_delta() < 0.0001:
      raise ValueError("Unity won't allow physics timesteps smaller than 0.0001")

    if self._ue.paused():
      self._update_engine_timing()



# def _approximate_integer_multiple(x, y):
#    modulo = x % y
#    return modulo < 1e-3
