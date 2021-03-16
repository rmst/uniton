

UNITON_VERSION = "0.2.0"
UNITON_DLL_VERSION = "0.2.0"
MAGIC_NUMBER = 1283621


# TODO: remove rpc class and expose constants directly
py = f"""\
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
# we write {{ to produce one curly brace
cs = f"""\
// This is a generated file. Do not modify manually.
namespace Uniton{{

  public static class Protocol{{
    public static string UNITON_VERSION = "{UNITON_VERSION}";
    public static int MAGIC_NUMBER = {MAGIC_NUMBER};
  }}
  
}}
"""


if __name__ == "__main__":

  import sys

  v = sys.argv[1]

  if v == 'py':
    print(py)
  elif v == 'cs':
    print(cs)
  elif v == 'version':
    print(UNITON_VERSION)