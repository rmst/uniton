

def removeprefix(s, prefix):
  # this is built into str from Python 3.9
  return s[len(prefix):] if s.startswith(prefix) else s


class BrokenPromiseException(Exception):
  pass


class RemoteException(Exception):
  pass