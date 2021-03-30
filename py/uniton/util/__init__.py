import sys
import os

def user_data_dir(appname):
  if sys.platform == "win32":
    data_dir = os.environ["CSIDL_APPDATA"]
  elif sys.platform == 'darwin':
    home = os.environ["HOME"]
    data_dir = f'{home}/Library/Application Support/'
  else:
    home = os.environ["HOME"]
    data_dir = os.environ.get('XDG_DATA_HOME', f"{home}/.local/share")

  return os.path.join(data_dir, appname)
