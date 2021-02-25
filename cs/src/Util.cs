using UnityEngine;
using UnityEngine.Rendering;

namespace Pysharp {

  public static class Log {

    public enum Level{
      VERBOSE = 0,
      DEBUG = 1,
      INFO = 2,
      ERROR = 3,
    }
    public static Level level = Level.DEBUG;
    public static void Print(string s, Level level = Level.DEBUG){
      if(level >= Log.level)
        UnityEngine.Debug.Log(s);
    }
  }


  public class RenderTools {
    // Camera basics
    // https://docs.unity3d.com/ScriptReference/Camera.Render.html

    // Camera properties TODO: read!
    // https://docs.unity3d.com/Manual/class-Camera.html


    // potentially switch to async gpu readbacks
    // https://docs.unity3d.com/ScriptReference/Rendering.AsyncGPUReadback.Request.html

    public static void RenderToTexture(Camera cam, ref Texture2D tex, Rect rect){
      // https://forum.unity.com/threads/rendering-gl-to-a-texture2d-immediately-in-unity4.158918/
      var rtex = RenderTexture.GetTemporary(tex.width, tex.height, 24, RenderTextureFormat.Default, RenderTextureReadWrite.Default);

      var r = cam.rect;
      var rtex_active = RenderTexture.active;
      var rtex_target = cam.targetTexture;

      cam.rect = rect; // make camera full screen https://docs.unity3d.com/ScriptReference/Camera-rect.html
      RenderTexture.active = rtex;
      cam.targetTexture = rtex;

      cam.Render();
      tex.ReadPixels(new Rect(0, 0, tex.width, tex.height), 0, 0);  // Read pixels from screen into the saved texture data.
      tex.Apply();  // Actually apply all previous SetPixel and SetPixels changes.
      
      cam.targetTexture = rtex_target;
      RenderTexture.active = rtex_active;
      cam.rect = r;

      RenderTexture.ReleaseTemporary(rtex);
    }


    // Async Readback requires Vulkan renderer on Linux (OpenGL doesn't work)
    public static AsyncGPUReadbackRequest RenderAsync(Camera cam){
      cam.Render();
      return AsyncGPUReadback.Request(cam.targetTexture);
    }
    
    public static byte[] PollReadbackRequest(AsyncGPUReadbackRequest req){
      req.WaitForCompletion();
      if (req.hasError){
        Log.Print("GPU readback error", Log.Level.ERROR);
      } else if (req.done) {
        var res = req.GetData<byte>().ToArray();
        return res;
      }

      return null;
    }

  }
}