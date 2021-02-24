import atexit
import socket
import struct
import threading
from queue import Queue
from threading import Thread
from typing import Sequence, Mapping


class rpc:
  GETMEMBER = 0
  INVOKE = 1
  GETOBJ = 2
  INIT = 3
  NOOP = 4
  FLOAT32 = 5
  STRING = 6
  INT32 = 7
  TUPLE = 8
  BOOL = 9
  OPEN_CMD_STREAM = 10
  BYTES = 11
  SETMEMBER = 12

  compatible_versions = (1,)


def serialize_objs(*args):  # TODO: rename to serialize_obj_ids
  # important: we need to create all RObjects and only afterwards query the ids
  # if we immediatly get the ids and then forget about each RObject, they will be garbage collected and ids might be reused
  obj = tuple(e if isinstance(e, CsObject) else RObject(e) for e in args)  # this can't be a generator because of the above reason
  ids = (e.id for e in obj)
  data = b"".join(SHOBJ.pack(id) for id in ids)
  return data


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

    # TODO: "get_Something" methods should be hidden and resolved to "Something"
    
    if (
      x in ("_ipython_canary_method_should_not_exist_", "_repr_mimebundle_") # this is needed for the ipython console
      or x.startswith('_')  # probably Python internal
    ):
      raise AttributeError()  
    id = self._con.cmd(rpc.GETMEMBER, serialize_objs(x, self))
    return CsObject(self._con, id)

  def __setattr__(self, k, v):
    if k in ("_con", "id"):
      return super().__setattr__(k, v)
    self._con.cmd(rpc.SETMEMBER, serialize_objs(self, k, v))

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
    id = self._con.cmd(rpc.INVOKE, serialize_objs(self, *args))
    return CsObject(self._con, id)

  def py(self):
    return self.to_py().wait()

  def to_py(self):
    return self._con.cmd(rpc.GETOBJ, serialize_objs(self), sync=True)

  def __str__(self):
    try:
      return "C# " + self._con.ToStr(self).py()
    except BrokenPromiseException as e:
      return "C# (Broken Promise)"

  def __repr__(self):
    return self.__str__()

  def __dir__(self):
    """
    TODO: this doesn't display properties with getters and setters correctly
    """
    r = super().__dir__()
    t = self.GetType()
    p = [m.Name.to_py() for m in t.GetMethods()]
    if t.IsSubclassOf(self._con.Type).py():
      p += [m.Name.to_py() for m in t.GetMethods()]

    p += [m.Name.to_py() for itf in t.GetInterfaces() for m in itf.GetMethods()]
    r += [m.wait() for m in p]
    return r


  def __del__(self):
    # del self._con.objs[self.id]
    # TODO: Notify the unity registry

    # print("Del ", self.id)

    # self._con.udel(self.id)
    self._con.delete_object(self.id)

  def __mul__(self, other):
    return self.op_Multiply(self, other)


default_connection = None
TLIST = (
  (int, rpc.INT32, struct.Struct("i")),
  (float, rpc.FLOAT32, struct.Struct("f")),
  (bool, rpc.BOOL, struct.Struct("?")),
)
TMAP = {x[0]: x[1:] for x in TLIST}
RMAP = {x[1]: x[2] for x in TLIST}
TCODE = struct.Struct("i")
SHOBJ = struct.Struct("i")  # should technically be I (unsigned int)


class RObject(CsObject):
  def __init__(self, x, con=None):
    con = default_connection if con is None else con

    # Serialization / Deserialization from bytes
    # https://docs.python.org/3.6/library/struct.html

    num_type = TMAP.get(type(x), None)
    if num_type is not None:
      rpc_fn, st = num_type
      # return rpc.Value(int32=x)
      id = con.cmd(rpc_fn, st.pack(x))
    elif isinstance(x, str):
      # return rpc.Value(str=x)
      id = con.cmd(rpc.STRING, x.encode())  # utf8
    # elif isinstance(x, bytes):
    #   return rpc.Value(bytes=x)
    # elif isinstance(x, bool):
    #   return rpc.Value(bool=x)
    # elif x is None:
    #   return rpc.Value(null=rpc.Null())
    elif isinstance(x, CsObject):
      raise AttributeError()  # TODO: copy on unity side

    elif isinstance(x, bytes):
      id = con.cmd(rpc.BYTES, x)

    elif isinstance(x, Sequence):
      print("sequence")
      # return rpc.Value(list=rpc.List(items=(self.deflate(e) for e in x)))
      id = con.cmd(rpc.TUPLE, serialize_objs(*x))
    else:
      raise AttributeError(f"Can't serialize {type(x)}")

    super().__init__(con, id)


class Promise:
  value = None

  def __init__(self, con):
    self.evt = threading.Event()
    self.con = con

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


class BrokenPromiseException(Exception):
  pass

class RemoteException(Exception):
  pass


class NamespaceOld:
  _con = None

  def __init__(self, con, ns=""):
    self._con = con
    self._namespace = ns
    

  def __getattr__(self, k):
    """
    we can cache these values because they are static
    """
    v = self._con.u.GetGlobalType(k, self._namespace)
    if v is not None:  # occurs after exceptions
      vars(self)[k] = v  # next time __getattr__ won't be called again
    return v


class Namespace:
  _con = None
  def __init__(self, con, ns=()):
    self._con = con
    self._ns = ns
    child_namespaces = [c.wait().split('.')[-1] for c in [c.to_py() for c in self._con.u.GetNamespaces('.'.join(self._ns))]]
    self._child_namespaces = [c for c in child_namespaces if c.isidentifier()]
    
  def __getattr__(self, k):
    if (
      k in ("_ipython_canary_method_should_not_exist_", "_repr_mimebundle_") # this is needed for the ipython console
      or k.startswith('_')  # probably Python internal
    ):
      raise AttributeError()  

    if k in self._child_namespaces:
      v = Namespace(self._con, ns=(*self._ns, k))
    else:
      v = self._con.u.GetTypeFromNamespace(k, '.'.join(self._ns))

    if v is not None:  # occurs after exceptions
      vars(self)[k] = v  # next time __getattr__ won't be called again
    return v

  def _typenames(self):
    typenames = [t.wait() for t in [t.to_py() for t in self._con.u.GetTypenames('.'.join(self._ns))]]
    return [t for t in typenames if t.isidentifier()]

  def __dir__(self):
    r = super().__dir__()
    r += self._typenames()
    r += self._child_namespaces
    r = list(set(r))
    return r


def recvall(sock, n):
  data = b''
  while len(data) < n:
    try:
      packet = sock.recv(n - len(data))
    except OSError:
      packet = None
    
    if not packet:
      return None
    data += packet
  return data


class Connection():
  rit = None
  return_thread = None
  cmd_queue = None
  sock = None
  def __init__(self):
    global default_connection
    default_connection = self
    self.id_c = 2  # the first two elements are manually set

    # channel = grpc.insecure_channel('localhost:50051')
    # self.remote = rpc.UnpyGrpcServiceStub(channel)
    # register(lambda: self.remote.Shutdown(rpc.Null()))

    HOST = '127.0.0.1'  # The server's hostname or IP address
    PORT = 11000        # The port used by the server

    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.connect((HOST, PORT))
    self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    remote_version, = struct.unpack('i', recvall(self.sock, 4))

    if remote_version not in rpc.compatible_versions:
      raise AttributeError(f"Remote version {remote_version} is not a compatible version. Must be in {rpc.compatible_versions}")

    atexit.register(self.close)

    self.garbage_objects = []

    # bootstrap
    self.Type = CsObject(self, id=0)
    self.u = CsObject(self, id=1)


    # self.udel = self.u.omap.Remove
    # self._del_objects = self.u.DelObjects

    # nice to have objects:
    self.ToStr = self.u.ToStr
    self.cs = Namespace(self)
    # self.ue = Namespace(self, "UnityEngine")
    # self.scene_manager = self.cs.SceneManager
    # self.scene = self.scene_manager.GetActiveScene()
    # self.GameObject = self.cs.GameObject
    # self.ReferenceEquals = self.cs.Object.ReferenceEquals
    # self.u.SetDebug(False)

  def close(self):
    atexit.unregister(self.close)
    if self.sock is not None:
      self.sock.close()

  def delete_object(self, x):
    self.garbage_objects.append(x)
    # print("del", x.id)

    # if len(self.garbage_objects) > 10000000:  # Don't delete because we recycle
    #   # print("garbage collect")
    #   ids = tuple(obj.id for obj in self.garbage_objects)  # also copy is necessary to avoid recursion
    #   self.garbage_objects.clear()
    #   self._del_objects(ids) # this will create new garbage

  def make_id(self):
    # print(tuple(x.id for x in self.garbage_objects))
    if self.garbage_objects:
      x = self.garbage_objects.pop()
      # print("recycle", x.id)
    else:
      x = self.id_c
      self.id_c += 1  # TODO: check for overflow
      # print('mk', x.id)
    return x


  def run_cmds(self):
    try:
      while True:
        # get length
        d = recvall(self.sock, 4)
        if d is None: break
        n, = struct.unpack('i', d)

        # get data
        d = recvall(self.sock, n)
        if d is None: break
        exc, = struct.unpack_from('i', d, 0)
        if exc:
          print("C# Exception:")
          # raise RemoteException(self.inflate(d[4:]))
          print(self.inflate(d[4:]))
          print("------------------\n")
          break
        else:
          # self.response_queue.put(self.inflate(d[4:]))
          p = self.promise_queue.get_nowait()
          assert p is not None, 'Received unexpected data from C#'
          p.resolve(self.inflate(d[4:]))
    finally:
      while not self.promise_queue.empty():
        p = self.promise_queue.get_nowait()
        p.resolve(BrokenPromiseException("A remote exception occured and the command stream was closed before this promise could be resolved."))

      # print("Shutting down return thread")

  def cmd_it(self):
    # TODO: remove this function? this is not used?
    self.sock.setblocking(0)  # will raise BlockingIOError
    while True:
      # get length
      try:
        d = recvall(self.sock, 4)
        if d is None: break
        n, = struct.unpack('i', d)

        # get data
        d = recvall(self.sock, n)
        if d is None: break
        exc, = struct.unpack_from('i', d, 0)
        if exc:
          print("Cmd stream close")
          raise RemoteException(self.inflate(d[4:]))
        else:
          # self.response_queue.put(self.inflate(d[4:]))
          p = self.promise_queue.get_nowait()
          p.resolve(self.inflate(d[4:]))
      except BlockingIOError:
        pass

      yield

    print("Shutting down return thread")

  def cmd(self, method, data, sync=False):
    # if self.rit is not None:
    #   try: next(self.rit)
    #   except StopIteration:
    #     self.rit = None
    if self.return_thread is None or not self.return_thread.is_alive():
      # if self.rit is None:
      # self.cmd_queue = Queue(1000)
      self.promise_queue = Queue()
      self.response_queue = Queue(1)
      self.return_thread = Thread(target=self.run_cmds, daemon=True)  # TODO: remove daemon and shut down properly
      self.return_thread.start()

      # self.rit = self.cmd_it()
      CsObject(self, self.cmd(rpc.OPEN_CMD_STREAM, b''))  # cmd stream open

    rid = 0 if sync else self.make_id()
    # self.cmd_queue.put(rpc.Cmd(method=method, rid=rid, args=self.deflate(args)))  # block if full
    data = struct.pack('ii', method, rid) + data
    # self.cmd_queue.put(rpc.Cmd(method=method, rid=rid, data=data))  # block if full

    data = struct.pack('i', len(data)) + data  # send length information

    if sync:
      # print("blocking!")
      # return self.response_queue.get()  # block

      # self.garbage_objects.append(rid) # prevent memory leak!

      res = Promise(self)
      self.promise_queue.put(res)
    else:
      res = rid

    self.sock.sendall(data)

    return res

  import sys
  assert sys.byteorder == "little", "We only support little endian systems"

  def inflate(self, x):
    # vi = x.WhichOneof("Value")
    # if vi == "list":
    #   return [self.inflate(e) for e in x.list.items]

    t, = TCODE.unpack_from(x)
    offset = TCODE.size
    if t in RMAP:
      r, = RMAP[t].unpack_from(x, offset)
      return r
    elif t == rpc.BYTES:
      return x[offset:]
    elif t == rpc.STRING:
      return x[offset:].decode("utf-8", "strict")
    else:
      raise AttributeError(f"Can't decode type {t}")

    # if vi == "obj":
    #   if x.obj.id not in self.objs:"
    #     cls = None if x.obj.tid == 0 else CsObject()
    #     r = CsObject(id=x.obj.id, _con=self)
    #     self.objs[x.obj.id] = weakref.ref(r)
    #     return r
      # else:
      #   return self.objs[x.obj.id]()

    # return getattr(x, vi)