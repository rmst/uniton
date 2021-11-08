import os
import sys
from uniton.util import user_data_dir
import shutil


def cmd_delete_data():
  d = user_data_dir('Uniton')
  shutil.rmtree(d, ignore_errors=True)
  print("Deleted all Uniton user data")

def cmd_open_data_dir():
  os.system(f"open '{user_data_dir('Uniton')}'")

def cmd_token():
  p = os.path.join(user_data_dir('Uniton'), 'token')
  if os.path.exists(p):
    print(open(p).read())
  else:
    print("You need to log in via the Unity Editor to get a token")

cmd = sys.argv[1] if len(sys.argv) > 1 else ''

cmds = {k[4:]: f for k, f in locals().items() if k.startswith("cmd_")}

if cmd not in cmds:
  print("You must provide on of the following commands:")
  print(*cmds.keys())
else:
  cmds[cmd](*sys.argv[2:])
