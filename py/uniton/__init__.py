import atexit
import subprocess

# from .unityproc import UnityProc
from .unityengine import UnityEngine

#
# class Uniton(Namespace):
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




def _monkey_patch_completer():
  # Avoid querying every object on autocomplete in the REPL.

  from .csobject import CsObject
  from .namespace import Namespace

  def patched_getattr(object, name, default=None):
    if isinstance(object, (CsObject, Namespace)):
      return None
      # raise AttributeError()
      # return getattr(object, name)
    else:
      return getattr(object, name, default)

  try:
    import rlcompleter
    rlcompleter.getattr = patched_getattr
  except:
    pass

  try:
    from jedi.inference.compiled import access
    access.getattr = patched_getattr
  except:
    pass

_monkey_patch_completer()
