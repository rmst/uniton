import atexit
import subprocess

from .connection import Connection
from .csobject import CsObject
from .namespace import Namespace


class Pysharp(Namespace):
  def __init__(self):
    c = Connection()
    super().__init__(c)

  def close(self):
    self._con.close()


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
