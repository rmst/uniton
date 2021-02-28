import atexit
import socket
import struct
from queue import Queue
from threading import Thread
from typing import Sequence

from .csobject import CsObject
from .protocol import rpc
from .util import BrokenPromiseException

TLIST = (
  (int, rpc.INT32, struct.Struct("i")),
  (float, rpc.FLOAT32, struct.Struct("f")),
  (bool, rpc.BOOL, struct.Struct("?")),
)
TMAP = {x[0]: x[1:] for x in TLIST}
RMAP = {x[1]: x[2] for x in TLIST}
TCODE = struct.Struct("i")
SHOBJ = struct.Struct("i")  # should technically be I (unsigned int)


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


import subprocess
from time import time


class UnityProc:
  """
  Representing a running Unity program
  Doubles as root namespace of that program, i.e. cs.System will return the 'System' namespace
  """

  _return_thread = None
  _cmd_queue = None
  _proc = None
  _sock = None

  def __init__(self, path=None, host=None, port=None):
    atexit.register(self.close)

    if path is not None:
      # TODO: find free port and set as env variable
      self._proc = subprocess.Popen([path])
      host = '127.0.0.1'
      port = 11001 if port is None else port
    else:
      host = '127.0.0.1' if host is None else host
      port = 11000 if port is None else port

    self._id_c = 2  # the first two elements are manually set

    # connect
    timeout = time() + 10

    while True:
      try:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((host, port))
        break
      except ConnectionRefusedError:
        if not self._proc:
          raise
        elif self._proc.poll() is not None:
          raise RuntimeError(f"Process {path} died before Uniton could connect!")
        elif time() > timeout:
          raise ConnectionRefusedError(f"Is {path} missing Uniton?")

    self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    # version compatibility check
    remote_version, = struct.unpack('i', recvall(self._sock, 4))

    if remote_version not in rpc.compatible_versions:
      raise AttributeError(f"Remote version {remote_version} is not a compatible version. Must be in {rpc.compatible_versions}")

    # init object management
    self._garbage_objects = []

    # bootstrap
    self._cs_type = CsObject(self, id=0)  # C# System.Type
    self._backend = CsObject(self, id=1)

    from .namespace import Namespace
    self._ns = Namespace(self)
    # from .unity_old import UnityEngine
    # self._ns.ue = self._ns.UnityEngine = UnityEngine(self)

    # self.Uniton.Log.level = 2  # only print INFO and ERROR

  @property
  def _pid(self):
    return self.System.Diagnostics.Process.GetCurrentProcess().Id

  def __getattr__(self, item):
    return getattr(self._ns, item)
    # return self._ns.__getattr__(item)  # Warning: this line breaks the namespace caching!

  def __dir__(self):
    return list(super().__dir__()) + dir(self._ns)

  def close(self):
    atexit.unregister(self.close)
    if self._sock is not None:
      self._sock.close()

    if self._proc is not None:
      self._proc.kill()

  def delete_object(self, x):
    self._garbage_objects.append(x)
    # print("del", x.id)

    # if len(self.garbage_objects) > 10000000:  # Don't delete because we recycle
    #   # print("garbage collect")
    #   ids = tuple(obj.id for obj in self.garbage_objects)  # also copy is necessary to avoid recursion
    #   self.garbage_objects.clear()
    #   self._del_objects(ids) # this will create new garbage

  def make_id(self):
    # print(tuple(x.id for x in self.garbage_objects))
    if self._garbage_objects:
      x = self._garbage_objects.pop()
      # print("recycle", x.id)
    else:
      x = self._id_c
      self._id_c += 1  # TODO: check for overflow
      # print('mk', x.id)
    return x

  def run_cmds(self):
    # TODO: make separate class for this
    try:
      while True:
        # get length
        d = recvall(self._sock, 4)
        if d is None: break
        n, = struct.unpack('i', d)

        # get data
        d = recvall(self._sock, n)
        if d is None: break
        exc, = struct.unpack_from('i', d, 0)
        if exc:
          # raise RemoteException(self.deserialize(d[4:]))
          print("C# " + self.deserialize(d[4:]))
          print("------------------\n")
          break
        else:
          # self.response_queue.put(self.deserialize(d[4:]))
          p = self.promise_queue.get_nowait()
          assert p is not None, 'Received unexpected data from C#'
          p.resolve(self.deserialize(d[4:]))
    finally:
      while not self.promise_queue.empty():
        p = self.promise_queue.get_nowait()
        p.resolve(BrokenPromiseException("The command stream was closed before this promise could be resolved."))

      # print("Shutting down return thread")

  def cmd(self, method, data, out=None):
    if self._return_thread is None or not self._return_thread.is_alive():
      # if self.rit is None:
      # self.cmd_queue = Queue(1000)
      self.promise_queue = Queue()
      self.response_queue = Queue(1)
      self._return_thread = Thread(target=self.run_cmds, daemon=True)  # TODO: remove daemon and shut down properly
      self._return_thread.start()

      # self.rit = self.cmd_it()
      CsObject(self, self.cmd(rpc.OPEN_CMD_STREAM, b''))  # cmd stream open

    rid = self.make_id() if out is None else 0  # if out is not None then remote object is sent and then  discarded

    # self.cmd_queue.put(rpc.Cmd(method=method, rid=rid, args=self.deflate(args)))  # block if full
    data = struct.pack('ii', method, rid) + data
    # self.cmd_queue.put(rpc.Cmd(method=method, rid=rid, data=data))  # block if full

    data = struct.pack('i', len(data)) + data  # send length information

    if out is None:
      out = rid
    else:
      # print("blocking!")
      # return self.response_queue.get()  # block
      # self.garbage_objects.append(rid) # prevent memory leak!

      self.promise_queue.put(out)

    self._sock.sendall(data)

    return out

  import sys
  assert sys.byteorder == "little", "We only support little endian systems"

  def deserialize(self, x):
    # vi = x.WhichOneof("Value")
    # if vi == "list":
    #   return [self.deserialize(e) for e in x.list.items]

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

  def serialize_objs(self, *args):  # TODO: rename to serialize_obj_ids
    # important: we need to create all RObjects and only afterwards query the ids
    # if we immediatly get the ids and then forget about each RObject, they will be garbage collected and ids might be reused
    obj = tuple(e if isinstance(e, CsObject) else self.tocs(e) for e in
                args)  # this can't be a generator because of the above reason
    ids = (e.id for e in obj)
    data = b"".join(SHOBJ.pack(id) for id in ids)
    return data
  
  def tocs(self, x):
    """Send Python object to C#"""
    # Serialization / Deserialization from bytes
    # https://docs.python.org/3.6/library/struct.html

    num_type = TMAP.get(type(x), None)
    if num_type is not None:
      rpc_fn, st = num_type
      # return rpc.Value(int32=x)
      id = self.cmd(rpc_fn, st.pack(x))
    elif isinstance(x, str):
      # return rpc.Value(str=x)
      id = self.cmd(rpc.STRING, x.encode())  # utf8
    # elif isinstance(x, bytes):
    #   return rpc.Value(bytes=x)
    # elif isinstance(x, bool):
    #   return rpc.Value(bool=x)
    # elif x is None:
    #   return rpc.Value(null=rpc.Null())
    elif isinstance(x, CsObject):
      raise AttributeError()  # TODO: copy on unity side

    elif isinstance(x, bytes):
      id = self.cmd(rpc.BYTES, x)

    elif isinstance(x, Sequence):
      print("sequence")
      # return rpc.Value(list=rpc.List(items=(self.deflate(e) for e in x)))
      id = self.cmd(rpc.TUPLE, self.serialize_objs(*x))
    else:
      raise AttributeError(f"Can't serialize {type(x)}")

    return CsObject(self, id)
