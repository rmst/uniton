import atexit
import socket
import struct
from queue import Queue
from threading import Thread
from typing import Sequence
from functools import lru_cache
import os
import subprocess
from time import time, sleep
from uniton.protocol import MAGIC_NUMBER
import uniton
from importlib import resources

class C:
  pass


self = C()


host = '127.0.0.1'
port = 11000

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
    else:
      sleep(0.1)  # wait, then repeat

# self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

self._sock.sendall(struct.pack("i", MAGIC_NUMBER))

dll = resources.read_binary(uniton, "uniton-pro.dll")

self._sock.sendall(struct.pack("i", len(dll)))
self._sock.sendall(dll)


