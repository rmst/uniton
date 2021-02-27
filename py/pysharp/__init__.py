import atexit
import subprocess

from .cs import Cs
# from .csobject import CsObject
# from .namespace import Namespace

#
# class Pysharp(Namespace):
#   def __init__(self):
#     c = Connection()
#     super().__init__(c)
#     self.unity = Unity(self)
#
#   def close(self):
#     self._con.close()


# class Unity(CsProc):
#   # def __init__(self, path=None, port=11000):
#   #   pass
#
#   _default_timescales = (1., 0.02, 0.)  # the real values will be set on stepping=True
#
#   @property
#   def stepping(self):
#     return self._backend.stepping.py()
#
#   @stepping.setter
#   def stepping(self, v):
#     t = self.UnityEngine.Time
#     if v:
#       self._default_timescales = (
#         t.timeScale,
#         t.fixedDeltaTime,
#         t.captureDeltaTime,
#       )
#       t.timeScale = 100  # Warning: 100 is the max value. if higher Unity will silently reject the change!
#       t.fixedDeltaTime = 0.02
#       t.captureDeltaTime = 0.02  # aligns Update and FixedUpdate
#     else:
#       (t.timeScale, t.fixedDeltaTime, t.captureDeltaTime) = self._default_timescales
#     self._backend.setStepping(v)
#
#   def step(self):
#     if "_step" not in vars(self):
#       self._step = self._backend.step
#     self._step()
#     # self._con.u.step()


# class Unity(Connection):
#   def __init__(self):
#     # TODO: create tmp dir, override $HOME and watch unity log paths (https://docs.unity3d.com/Manual/LogFiles.html)
#     self.proc = subprocess.Popen(["/home/simon/dev/unpy/unity/bin/unpy.x86_64"])
#     import time
#     atexit.register(self.proc.kill)
#     time.sleep(10)
#     super().__init__()


def _monkey_path_rlcompleter():
  # Avoid querying every object on autocomplete in the REPL. It's silly behaviour by rlcompleter anyway.

  import rlcompleter

  def patched_getattr(obj, k):
    if isinstance(obj, (CsObject, Namespace)):
      return None
    else:
      return getattr(obj, k)

  rlcompleter.getattr = patched_getattr


_monkey_path_rlcompleter()
