
# TODO: all of the protocol should be in a JSON file

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