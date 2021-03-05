

def removeprefix(s, prefix):
  # this is built into str from Python 3.9
  return s[len(prefix):] if s.startswith(prefix) else s


class BrokenPromiseException(Exception):
  pass


class RemoteException(Exception):
  pass


def topy(x):
  if isinstance(x, (list, tuple)):
    x = [e.py for e in x]  # request all
    return [e.wait() for e in x]  # wait all

  raise AttributeError(f"Objects like {x} are not supported")