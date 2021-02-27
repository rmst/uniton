import threading

from pysharp.protocol import rpc
from pysharp.util import removeprefix, BrokenPromiseException, RemoteException


class Promise:
  value = None

  def __init__(self):
    self.evt = threading.Event()

  def resolve(self, x):
    self.value = x
    self.evt.set()

  def __call__(self):
    return self.wait()

  def wait(self):
    self.evt.wait()
    # while self.value is None:
    #   next(self.con.rit)

    if isinstance(self.value, BrokenPromiseException):
      raise self.value

    return self.value


GETATTR_BLACKLIST = (
  "_ipython_canary_method_should_not_exist_",  # ipython console uses this
  "_repr_mimebundle_",  # ipython console uses this
)


# noinspection PyProtectedMember
class CsObject:
  cs = None
  id = None

  def __init__(self, cs, id):
    self.cs = cs
    self.id = id

  def __getattr__(self, k: str):
    if k.startswith('_') or k in GETATTR_BLACKLIST:
      raise AttributeError()

    id = self.cs.cmd(rpc.GETMEMBER, self.cs.serialize_objs(k, self))
    return CsObject(self.cs, id)

  def __setattr__(self, k, v):
    if k in ("cs", "id") or k.startswith('_') or k in GETATTR_BLACKLIST:
      return super().__setattr__(k, v)

    self.cs.cmd(rpc.SETMEMBER, self.cs.serialize_objs(self, k, v))

  def __getitem__(self, k):
    return self.get_Item(k)

  def __setitem__(self, k, v):
    return self.set_Item(k, v)

  def __iter__(self):
    for i in range(len(self)):
      yield self[i]

  def __len__(self):
    return self.Count.py()

  def __bool__(self):
    return self.py()

  def __call__(self, *args):
    # TODO: better error message for wrong argument types
    # return self._con.cmd(rpc.INVOKE, (self, args))
    id = self.cs.cmd(rpc.INVOKE, self.cs.serialize_objs(self, *args))
    return CsObject(self.cs, id)

  @property
  def py(self):
    out = None
    out = Promise() if out is None else out
    return self.cs.cmd(rpc.GETOBJ, self.cs.serialize_objs(self), out=out)

  def __str__(self):
    try:
      return "C# " + self.cs._backend.ToStr(self).py()
    except BrokenPromiseException as e:
      # return "C# (Broken Promise)"
      return ""
    except:
      return ""

  def __repr__(self):
    return self.__str__()

  def __dir__(self):
    try:
      t = self.GetType()

      if t.IsSubclassOf(self.cs._cs_type).py():
        # self is a type
        x = [m.Name.py for m in self.GetMethods()]
      else:
        x = [m.Name.py for m in t.GetMethods()]
        x += [m.Name.py for itf in t.GetInterfaces() for m in itf.GetMethods()]

      x = (m.wait() for m in x)
      x = (removeprefix(e, "get_") for e in x)
      x = (removeprefix(e, "set_") for e in x)
      x = set(x)
      x = (e for e in x if e.isidentifier())
    except RemoteException:
      x = []

    r = super().__dir__()
    r += list(x)
    return r

  def __del__(self):
    # del self._con.objs[self.id]
    # TODO: Notify the unity registry

    # print("Del ", self.id)

    # self._con.udel(self.id)
    self.cs.delete_object(self.id)

  def __mul__(self, other):
    return self.op_Multiply(self, other)

  # TODO: add more operators



