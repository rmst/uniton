from .unityproc import UnityProc


# noinspection PyProtectedMember
class UnityEngine(UnityProc):
  _default_timescales = (1., 0.02, 0.)  # the real values will be set on stepping=True

  # def __init__(self, ue):
  #   super().__init__(ue, "UnityEngine")

  def pause(self):
    self._default_timescales = (
      self.Time.timeScale,
      self.Time.fixedDeltaTime,
      self.Time.captureDeltaTime,
    )
    self.Time.timeScale = 100  # Warning: 100 is the max value. if higher Unity will silently reject the change!
    self.Time.fixedDeltaTime = 0.02
    self.Time.captureDeltaTime = 0.02  # aligns Update and FixedUpdate
    self._backend.setStepping(True)

  def paused(self):
    return self._backend.stepping.py()

  def resume(self):
    (self.Time.timeScale, self.Time.fixedDeltaTime, self.Time.captureDeltaTime) = self._default_timescales
    self._backend.setStepping(False)

  def step(self):
    if "_step" not in vars(self):
      self._step = self._backend.step
    self._step()