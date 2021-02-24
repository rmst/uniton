import atexit
import subprocess

from .connection import Connection


class Unity(Connection):
  def __init__(self):
    # TODO: create tmp dir, override $HOME and watch unity log paths (https://docs.unity3d.com/Manual/LogFiles.html)
    self.proc = subprocess.Popen(["/home/simon/dev/unpy/unity/bin/unpy.x86_64"])
    import time
    atexit.register(self.proc.kill)
    time.sleep(10)
    super().__init__()


if __name__ == '__main__':
  # Unity()
  # from IPython import embed
  # embed()


  for a in range(5):
    if a in (1, 3):
      print(a)
