from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile
from os.path import join, exists
import sys
from subprocess import call

# from uniton.util.appdirs import user_cache_dir
from uniton.protocol import UNITON_VERSION
from uniton import UnityEngine
from uniton.util import user_data_dir

CACHE_DIR = user_data_dir("Uniton")
# TODO: delete older version binaries to save space


def download_and_unzip(url, dest):
  http_response = urlopen(url)
  zipfile = ZipFile(BytesIO(http_response.read()))
  zipfile.extractall(path=dest)


class ExampleEnv(UnityEngine):
  def __init__(self, host=None, port=None):
    super().__init__(get_bin(self), host, port)


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


BIN_VERSION = '0.3.0'


class Empty(ExampleEnv):
  class darwin:
    url = f"https://github.com/uniton-dev/uniton/releases/download/v{BIN_VERSION}/empty_mac.zip"
    path = join(CACHE_DIR, "empty.app")
    bin = join(CACHE_DIR, "empty.app", "Contents", "MacOS", "Empty")
  class linux:
    url = f"https://github.com/uniton-dev/uniton/releases/download/v{BIN_VERSION}/empty_linux.zip"
    path = join(CACHE_DIR, "empty")
    bin = join(CACHE_DIR, "empty", "Empty.x86_64")
  class win32:
    url = f"https://github.com/uniton-dev/uniton/releases/download/v{BIN_VERSION}/empty_windows.zip"
    path = join(CACHE_DIR, "empty")
    bin = join(CACHE_DIR, "empty", "Empty.exe")


class Kart(ExampleEnv):
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


class Temple(ExampleEnv):
  class darwin:
    url = f"https://github.com/uniton-dev/uniton/releases/download/v{BIN_VERSION}/temple_mac.zip"
    path = join(CACHE_DIR, "temple.app")
    bin = join(CACHE_DIR, "temple.app", "Contents", "MacOS", "Temple")
  class linux:
    url = f"https://github.com/uniton-dev/uniton/releases/download/v{BIN_VERSION}/temple_linux.zip"
    path = join(CACHE_DIR, "temple")
    bin = join(CACHE_DIR, "temple", "temple.x86_64")
  class win32:
    url = f"https://github.com/uniton-dev/uniton/releases/download/v{BIN_VERSION}/temple_windows.zip"
    path = join(CACHE_DIR, "temple")
    bin = join(CACHE_DIR, "temple", "Temple.exe")
    


class FloodedGrounds(ExampleEnv):
  class darwin:
    url = f"https://github.com/uniton-dev/uniton/releases/download/v{BIN_VERSION}/floodedgrounds_mac.zip"
    path = join(CACHE_DIR, "floodedgrounds.app")
    bin = join(CACHE_DIR, "floodedgrounds.app", "Contents", "MacOS", "Floodedgrounds")
  class linux:
    url = f"https://github.com/uniton-dev/uniton/releases/download/v{BIN_VERSION}/floodedgrounds_linux.zip"
    path = join(CACHE_DIR, "floodedgrounds")
    bin = join(CACHE_DIR, "floodedgrounds", "floodedgrounds.x86_64")
  class win32:
    url = f"https://github.com/uniton-dev/uniton/releases/download/v{BIN_VERSION}/floodedgrounds_windows.zip"
    path = join(CACHE_DIR, "floodedgrounds")
    bin = join(CACHE_DIR, "floodedgrounds", "Floodedgrounds.exe")



class WindridgeCity(ExampleEnv):
  class darwin:
    url = f"https://github.com/uniton-dev/uniton/releases/download/v{BIN_VERSION}/windridgecity_mac.zip"
    path = join(CACHE_DIR, "windridgecity.app")
    bin = join(CACHE_DIR, "windridgecity.app", "Contents", "MacOS", "Windridgecity")
  class linux:
    url = f"https://github.com/uniton-dev/uniton/releases/download/v{BIN_VERSION}/windridgecity_linux.zip"
    path = join(CACHE_DIR, "windridgecity")
    bin = join(CACHE_DIR, "windridgecity", "windridgecity.x86_64")
  class win32:
    url = f"https://github.com/uniton-dev/uniton/releases/download/v{BIN_VERSION}/windridgecity_windows.zip"
    path = join(CACHE_DIR, "windridgecity")
    bin = join(CACHE_DIR, "windridgecity", "Windridgecity.exe")


class Forest(ExampleEnv):
  class darwin:
    url = f"https://github.com/uniton-dev/uniton/releases/download/v{BIN_VERSION}/forest_mac.zip"
    path = join(CACHE_DIR, "forest.app")
    bin = join(CACHE_DIR, "forest.app", "Contents", "MacOS", "Forest")
  class linux:
    url = f"https://github.com/uniton-dev/uniton/releases/download/v{BIN_VERSION}/forest_linux.zip"
    path = join(CACHE_DIR, "forest")
    bin = join(CACHE_DIR, "forest", "forest.x86_64")
  class win32:
    url = f"https://github.com/uniton-dev/uniton/releases/download/v{BIN_VERSION}/forest_windows.zip"
    path = join(CACHE_DIR, "forest")
    bin = join(CACHE_DIR, "forest", "Forest.exe")