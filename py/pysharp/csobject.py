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

  def wait(self):
    self.evt.wait()
    # while self.value is None:
    #   next(self.con.rit)

    if isinstance(self.value, BrokenPromiseException):
      raise self.value

    return self.value


class CsObject:
  _con = None
  id = None

  def __init__(self, con, id):
    self._con = con
    self.id = id

  # _con: Connection
  # _type: CsObject = None
  # def __init__(self):

  # def __getattr__(self, k):
  #     self._con.invoke(self.class.utype)

  def __getattr__(self, x: str):
    # print(x, y)
    # self._con.remote.ACall.future(rpc.ACallRequest(method=rpc.GETMEMBER, rid=rid, args=y))
    # return self._con.cmd(rpc.GETMEMBER, (x, self))

    if (
      x in ("_ipython_canary_method_should_not_exist_", "_repr_mimebundle_") # this is needed for the ipython console
      or x.startswith('_')  # probably Python internal
    ):
      raise AttributeError()
    id = self._con.cmd(rpc.GETMEMBER, self._con.serialize_objs(x, self))
    return CsObject(self._con, id)

  def __setattr__(self, k, v):
    if k in ("_con", "id"):
      return super().__setattr__(k, v)
    self._con.cmd(rpc.SETMEMBER, self._con.serialize_objs(self, k, v))

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
    id = self._con.cmd(rpc.INVOKE, self._con.serialize_objs(self, *args))
    return CsObject(self._con, id)

  def py(self):
    return self.to_py().wait()

  def to_py(self, out=None):
    out = Promise() if out is None else out
    return self._con.cmd(rpc.GETOBJ, self._con.serialize_objs(self), out=out)

  def __str__(self):
    try:
      return "C# " + self._con.ToStr(self).py()
    except BrokenPromiseException as e:
      # return "C# (Broken Promise)"
      return ""
    except:
      return ""

  def __repr__(self):
    return self.__str__()

  def __dir__(self):
    """
    TODO: this doesn't display static functions / members afaik
    """
    try:
      t = self.GetType()

      if t.IsSubclassOf(self._con.Type).py():
        # self is a type
        x = [m.Name.to_py() for m in self.GetMethods()]
      else:
        x = [m.Name.to_py() for m in t.GetMethods()]
        x += [m.Name.to_py() for itf in t.GetInterfaces() for m in itf.GetMethods()]

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
    self._con.delete_object(self.id)

  def __mul__(self, other):
    return self.op_Multiply(self, other)





