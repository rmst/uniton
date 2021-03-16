from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile
from os.path import join, exists
import sys
from subprocess import call

from uniton.util.appdirs import user_cache_dir
from uniton.protocol import UNITON_VERSION
from uniton import UnityEngine


CACHE_DIR = user_cache_dir("uniton", "uniton-dev", UNITON_VERSION)
# TODO: delete older version binaries to save space


def download_and_unzip(url, dest):
  http_response = urlopen(url)
  zipfile = ZipFile(BytesIO(http_response.read()))
  zipfile.extractall(path=dest)


BIN_VERSION = '0.2.0'

class Kart:
  class darwin:
    url = f"https://github.com/uniton-dev/uniton/releases/download/v{BIN_VERSION}/kart_mac.zip"
    path = join(CACHE_DIR, "kart.app")
    bin = join(CACHE_DIR, "kart.app", "Contents", "MacOS", "Kart")
  class linux:
    url = f"https://github.com/uniton-dev/uniton/releases/download/v{BIN_VERSION}/kart_linux.zip"
    path = join(CACHE_DIR, "kart")
    bin = join(CACHE_DIR, "kart", "kart.x86_64")
  class win32:
    url = f"https://github.com/uniton-dev/uniton/releases/download/v{BIN_VERSION}/kart_windows.zip"
    path = join(CACHE_DIR, "kart")
    bin = join(CACHE_DIR, "kart", "Kart.exe")


class Temple:
  class darwin:
    url = f"https://github.com/uniton-dev/uniton/releases/download/v{BIN_VERSION}/temple_mac.zip"
    path = join(CACHE_DIR, "temple.app")
    bin = join(CACHE_DIR, "temple.app", "Contents", "MacOS", "Kart")
  class linux:
    url = f"https://github.com/uniton-dev/uniton/releases/download/v{BIN_VERSION}/temple_linux.zip"
    path = join(CACHE_DIR, "kart")
    bin = join(CACHE_DIR, "temple", "temple.x86_64")
  class win32:
    url = f"https://github.com/uniton-dev/uniton/releases/download/v{BIN_VERSION}/temple_windows.zip"
    path = join(CACHE_DIR, "kart")
    bin = join(CACHE_DIR, "kart", "kart", "Kart.exe")
    


def get_bin(cls):
  x = getattr(cls, sys.platform)
  if not exists(x.path):
    print(f"Downloading {x.url} to {x.path} ...")
    download_and_unzip(x.url, x.path)
    
    # make exectutable
    if sys.platform in ('darwin', 'linux'):
      call(["chmod", "+x", x.bin])
    # TODO: do we need to do anything on windows?

  return x.bin


class KartGame(UnityEngine):
  def __init__(self, host=None, port=None):
    super().__init__(get_bin(Kart), host, port)