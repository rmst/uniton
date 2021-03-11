using UnityEngine;
using UnityEngine.Rendering;
using System;
using Unity.Collections;


 #if UNITY_EDITOR
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using System.Reflection;

class MyCustomBuildProcessor : IPreprocessBuildWithReport
{
    public int callbackOrder { get { return 0; } }
    public void OnPreprocessBuild(BuildReport report)
    {
        Debug.Log("MyCustomBuildProcessor.OnPreprocessBuild for target " + report.summary.platform + " at path " + report.summary.outputPath);
        // Debug.Log("" + Assembly.GetExecutingAssembly().Location);

    }
}
 #endif


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

  public class RenderQueue{
    AsyncGPUReadbackRequest?[] requests;  // for some reason Async... is not nullable so we need the '?'
    byte[][] completed_frames;
    int step = 0;
    int size;
    public RenderQueue(int size){
      this.size = size;
      this.requests = new AsyncGPUReadbackRequest?[size];
      this.completed_frames = new byte[size][];
    }

    public byte[] Render(Camera cam){
      cam.Render();
      this.requests[this.step % this.size] = AsyncGPUReadback.Request(cam.targetTexture);
      var oldest = (this.step+1) % this.size;  // the index for the oldest request

      for(int i=0; i < this.size; i++){
        if(requests[i].HasValue){
          var req = requests[i].Value;  // .Value comes from Nullable<>
          if(i == oldest)
            req.WaitForCompletion();
          else
            req.Update();
          if (req.hasError){
            throw new Exception("GPU readback error");
          } else if (req.done) {
            var res = req.GetData<byte>().ToArray();
            this.completed_frames[i] = res;
            this.requests[i] = null;
          }
        }
      }

      var frame = this.completed_frames[oldest];

      this.step += 1;
      return frame is null ? new byte[]{} : frame;  // because null not serializable atm
    }
  }

    public class RenderQueue2{
      // not faster than normal RenderQueue
    AsyncGPUReadbackRequest?[] requests;  // for some reason Async... is not nullable so we need the '?'
    byte[][] completed_frames;
    int step = 0;
    int size;
    public RenderQueue2(int size, int framesize){
      this.size = size;
      this.requests = new AsyncGPUReadbackRequest?[size];
      this.completed_frames = new byte[size][];
      for(var i=0; i < this.completed_frames.Length; i++)
        this.completed_frames[i] = new byte[framesize];
    }

    public byte[] Render(Camera cam){
      cam.Render();
      this.requests[this.step % this.size] = AsyncGPUReadback.Request(cam.targetTexture);
      var oldest = (this.step+1) % this.size;  // the index for the oldest request

      for(int i=0; i < this.size; i++){
        if(requests[i].HasValue){
          var req = requests[i].Value;  // .Value comes from Nullable<>
          if(i == oldest)
            req.WaitForCompletion();
          else
            req.Update();
          if (req.hasError){
            throw new Exception("GPU readback error");
          } else if (req.done) {
            // req.GetData<byte>().CopyTo(this.completed_frames[i]);
            var na = req.GetData<byte>();

            // convert RGBA to RGB
            for(var j=0; j < na.Length/4; j++){
              NativeArray<byte>.Copy(na, j*4, this.completed_frames[i], j*3, 3);
            }
            
            na.Dispose();
            this.requests[i] = null;
          }
        }
      }

      var frame = this.completed_frames[oldest];

      this.step += 1;
      return frame;
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
    

    public static byte[] WaitReadbackRequest(AsyncGPUReadbackRequest req){
      req.WaitForCompletion();
      // Warning: This will fail if this method is called too late. The result is only available for one frame
      if (req.hasError){
        // Log.Print("GPU readback error", Log.Level.ERROR);
        throw new Exception("GPU readback error");
      } else if (req.done) {
        var res = req.GetData<byte>().ToArray();
        return res;
      }
      throw new Exception("Strange GPU readback error");
    }

    public static byte[] PollReadbackRequest(AsyncGPUReadbackRequest req){
      req.Update();
      if (req.hasError){
        Log.Print("GPU readback error", Log.Level.ERROR);
      } else if (req.done) {
        var res = req.GetData<byte>().ToArray();
        return res;
      }
      // Log.Print("Empty");
      return new byte[]{};
    }
  }




  // public class RenderQueue{
  //   AsyncGPUReadbackRequest[] q;
  //   RenderTexture[] t;
  //   int i = 0;
  //   Camera c;

  //   public RenderQueue(Camera camera, RenderTexture[] textures){
  //     c = camera;
  //     t = textures;
  //     q = new AsyncGPUReadbackRequest[t.Length];
  //   }

  //   public Update(){
  //     cam.targetTexture = t[i];
  //     q[i] = cam.Render();

  //     if(q[(i+q.Length-1)] != null){

  //     }
  //   }
  // }
}