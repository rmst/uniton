using UnityEngine;
using UnityEngine.Rendering;
using System;
using Unity.Collections;





namespace Uniton {


  public static class Util {
    public static object nullreference = null;
  }


  public static class Log {
    public enum Level{
      VERBOSE = 0,
      DEBUG = 1,
      INFO = 2,
      ERROR = 3,
    }
    public static Level level = Level.INFO;
    public static void Print(string s, Level level = Level.DEBUG){
      if(level >= Log.level)
        UnityEngine.Debug.Log(s);
    }
  }
}