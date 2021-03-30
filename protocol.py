from os.path import dirname, join

CS = join(dirname(__file__), 'cs')
PY = join(dirname(__file__), 'py')


UNITON_VERSION = "0.3.6"
# UNITON_DLL_VERSION = "0.3.0"
MAGIC_NUMBER = 1283621

skip_dll_bytes = 239


def replace_all(variables: dict, template: str):
  for k, v in variables.items():
    template = template.replace(f"<<<{k}>>>", v)

  return template


# TODO: remove rpc class and expose constants directly
def template_py():
  return f"""\
# This is a generated file. Do not modify manually.

UNITON_VERSION = "{UNITON_VERSION}"
MAGIC_NUMBER = {MAGIC_NUMBER}

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

"""


# TODO: add more of the protocol below
# in format string f"..." we can write {{ to produce one curly brace

def template_cs(namespace="Uniton"):
  return f"""\
// This is a generated file. Do not modify manually.
namespace {namespace}{{

  public static class Protocol{{
    public static string UNITON_VERSION = "{UNITON_VERSION}";
    public static int MAGIC_NUMBER = {MAGIC_NUMBER};
  }}
  
}}
"""


# def py():
#   open(PY+"/uniton/protocol.py", "w").write(template_py())
#
#
# def cs():
#   open(CS + "/src/_Protocol.cs", "w").write(template_cs("Uniton"))
#   open(CS + "/src/bootstrap/_Protocol.cs", "w").write(template_cs("Uniton.Bootstrap"))
#   open(CS + "/src/editor/_Protocol.cs", "w").write(template_cs("Uniton.Editor"))
#
#
# if __name__ == "__main__":
#   py()
#   cs()
