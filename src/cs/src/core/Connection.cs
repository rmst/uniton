using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;
using System.Text;  // Encoding
using System.Threading.Tasks;
using System.Runtime.CompilerServices;
using System.Reflection;
using System;
using System.Collections.Concurrent;
using System.Net.Sockets;
using System.Net;
using System.Linq;
using System.Threading;


namespace Uniton{
  class InflatedNull {}
  class DontStore {}

  enum CmdType{
    // TODO: put whole IPC spec in JSON
    GETMEMBER = 0,
    INVOKE = 1,
    GETOBJ = 2,
    INIT = 3,
    NOOP = 4,
    FLOAT32 = 5,
    STRING = 6,
    INT32 = 7,
    TUPLE = 8,
    BOOL = 9,
    OPEN_CMD_STREAM = 10,

    BYTES = 11,
    SETMEMBER = 12,
  }


  class Connection : MonoBehaviour{
    public int obj_id_gen = 1;  // start with 1 because 0 is protobuf default/empty
    DontStore DONTSTORE = new DontStore();
    InflatedNull NONE = new InflatedNull();  // TODO: rename to INFLATED_NULL
    // Dictionary<int, object> omap = new Dictionary<int, object>();
    public List<object> sho;
    public ulong updates = 0;
    public ulong fixed_updates = 0;

    public bool step_next;
    public bool stepping;

    public Texture2D overlay = null; // TODO: check and delete

    IEnumerator cmd_stream;

    bool cmd_stream_closed = true;
  


    // public Connection(){
    //   // this.cmd_stream = this.ConnectionLoop();
    
    // }

    public void Awake(){
      DontDestroyOnLoad(this.gameObject);

      // Creating and destroying the main coroutine. We use coroutines i.e. IEnumerator, because async-await doesn't seem to free resources adequately in Unity.
      this.cmd_stream = this.CmdStream();
    }
    public void FixedUpdate() {
      // cmd_stream.MoveNext();
      fixed_updates ++;

    }

    public void Update(){
      cmd_stream.MoveNext();
      updates ++;
    }

    public void OnDestroy(){
      // ((IDisposable)this.cmd_stream).Dispose();  // without this the finally block won't be executed!
      Type S = GetTypeByFullName("Uniton.Bootstrap.SocketBox");
      var socket = (Socket) S.GetField("socket").GetValue(null);
      socket.Close();
    }

    public void OnGUI(){
      // TODO : what is this?
      if (overlay != null)
        GUI.DrawTexture(new Rect(0, 0, Screen.width, Screen.height), overlay, ScaleMode.ScaleToFit);
    }


    object[] mk_obj_array(byte[] a, int start, int stop){
      var num = (stop - start)/4;
      object[] ret = new object[num];
      for(int i = 0; i < num; i++){
        ret[i] = mk_obj(a, start + i * 4);
      }
      return ret;
    }

    object mk_obj(byte[] a, int offset){
        var id = BitConverter.ToInt32(a, offset);
        // return sho[id];
        return GetObject(id);
    }
    
    void exec_cmd(byte[] data){
      object z = null;
      // var data = r.Data.ToByteArray();

      var method = BitConverter.ToInt32(data, 0);
      var rid = BitConverter.ToInt32(data, 4);
      Log.Print("Cmd: method=" + method + " rid=" + rid);

      if(cmd_stream_closed){
        if((CmdType)method == CmdType.OPEN_CMD_STREAM){  // reopen cmd stream
          cmd_stream_closed = false;
          Log.Print("Command stream open");
          z = NONE;
        } else {
          Log.Print("Cmd ignored");
          z = NONE;  // prevent invalid memory access
        }
      } else {
        var HL = 8;
        try {
          // var args = Infl(r.Args);
          switch((CmdType)method){
            case CmdType.GETMEMBER: z = GetMember((string)mk_obj(data, HL), mk_obj(data, HL+4)); break;
            case CmdType.SETMEMBER: z = NONE; SetMember(mk_obj(data, HL), (string)mk_obj(data, HL+4), mk_obj_array(data, HL+8, data.Length)); break;
            case CmdType.INVOKE: z = Invoke(mk_obj(data, HL), mk_obj_array(data, HL+4, data.Length)); break;
            case CmdType.GETOBJ: z = NONE; send_back(mk_obj(data, HL), 0); break;
            case CmdType.FLOAT32: z = BitConverter.ToSingle(data, HL); break;
            case CmdType.STRING: z = Encoding.UTF8.GetString(data, HL, data.Length-HL); break;
            case CmdType.INT32: z = BitConverter.ToInt32(data, HL); break;
            case CmdType.TUPLE: z = mk_obj_array(data, HL, data.Length); break;
            case CmdType.BOOL: z = BitConverter.ToBoolean(data, HL); break;
            case CmdType.BYTES: z = ArrayCopy(data, HL, data.Length); break;
          }
          // TODO: raise error
          // Debug.Log( " " + args + " " + ret + " " + z);
        } catch (Exception exc) {
          // Debug.Log("Exception");
          if(exc is System.Reflection.TargetInvocationException){
            exc = exc.InnerException;
          }

          Log.Print("" + exc);
          // result_queue.WriteAsync(new ReturnValue {Exception=2, Obj=Defl(z.ToString())}).Wait();  // Exception=2 means the exception occured during an async call
          // result_queue.WriteAsync(new ReturnValue {Exception=2, Data=ByteString.CopyFrom(serialize(z.ToString()))}).Wait();

          send_back(exc.ToString(), 2);
          // throw (Exception)z;
          cmd_stream_closed = true;
          Log.Print("Command stream close");
          z = NONE;
        }
      }

      if(rid != 0)
        AddObject(rid, z);
    }



    public IEnumerator CaptureFrames(){
      // TODO: is this used??

      // Start this via `StartCoroutine(CaptureFrames());`
      // https://docs.unity3d.com/ScriptReference/WaitForEndOfFrame.html

      // We should only read the screen buffer after rendering is complete
      yield return new WaitForEndOfFrame();

      // // Create a texture the size of the screen, RGB24 format
      // int width = Screen.width;
      // int height = Screen.height;
      // Texture2D tex = new Texture2D(width, height, TextureFormat.RGB24, false);

      // // Read screen contents into the texture
      // tex.ReadPixels(new Rect(0, 0, width, height), 0, 0);
      // tex.Apply();

      // // Encode texture into PNG
      // byte[] bytes = tex.EncodeToPNG();
      // Destroy(tex);

    }

    // public byte[] serialize_single<T>(int t, T x) where T: struct{
    //   return Concat(BitConverter.GetBytes(t), BitConverter.GetBytes(x));
    // }

    ArraySegment<byte> getseg(int x){ return new ArraySegment<byte>(BitConverter.GetBytes(x));}
    ArraySegment<byte> getseg(float x){ return new ArraySegment<byte>(BitConverter.GetBytes(x));}
    ArraySegment<byte> getseg(bool x){ return new ArraySegment<byte>(BitConverter.GetBytes(x));}
    ArraySegment<byte> getseg(byte[] x){ return new ArraySegment<byte>(x);}
    ArraySegment<byte> getseg(string x){ return new ArraySegment<byte>(Encoding.UTF8.GetBytes(x));}

    public byte[] serialize(object x){
      // TODO: remove, seems obsolete
      if(x is int) return Concat(BitConverter.GetBytes((int) CmdType.INT32), BitConverter.GetBytes((int) x));
      else if(x is float) return Concat(BitConverter.GetBytes((int) CmdType.FLOAT32), BitConverter.GetBytes((float) x));
      else if(x is bool) return Concat(BitConverter.GetBytes((int) CmdType.BOOL), BitConverter.GetBytes((bool) x));
      else if(x is string) return Concat(BitConverter.GetBytes((int) CmdType.STRING), Encoding.UTF8.GetBytes((string) x));
      else if(x is byte[]) return Concat(BitConverter.GetBytes((int) CmdType.BYTES), (byte[]) x);

      throw new ArgumentException("Object " + ToStr(x) + " of type '" + x.GetType().FullName + "' is not serializable");
    }

    public void serialize(object x, ref ArraySegment<byte>[] sbb){
      if(x is int) {sbb[2] = getseg((int) CmdType.INT32); sbb[3] = getseg((int) x);}
      else if(x is float) {sbb[2] = getseg((int) CmdType.FLOAT32); sbb[3] = getseg((float) x);}
      else if(x is bool) {sbb[2] = getseg((int) CmdType.BOOL); sbb[3] = getseg((bool) x);}
      else if(x is string) {sbb[2] = getseg((int) CmdType.STRING); sbb[3] = getseg((string) x);}
      else if(x is byte[]) {sbb[2] = getseg((int) CmdType.BYTES); sbb[3] = getseg((byte[]) x);}
      else throw new ArgumentException("Object " + ToStr(x) + " not serializable");
    }

    ArraySegment<byte>[] sbb = new ArraySegment<byte>[4];
    public void send_back(object x, int exception){    
      // var data = Concat(BitConverter.GetBytes(exception), serialize(x));
      // data = Concat(BitConverter.GetBytes(data.Length), data);
      // var n = socket.Send(data);
      if(this.socket == null)
        return;
      
      sbb[1] = getseg(exception);
      serialize(x, ref sbb);
      sbb[0] = getseg(sbb[1].Count + sbb[2].Count + sbb[3].Count);
      var n = this.socket.Send(sbb);
      // if(n != sbb[0].Count + sbb[1].Count + sbb[2].Count + sbb[3].Count){
      //   Debug.Log("Error only sent " + n);
      // }

      // if(n != data.Length){
      //   Debug.Log("Error: Needed to send " + data.Length + "bytes but sent only " + n);
      // }
      // result_queue.WriteAsync(new ReturnValue {Data=ByteString.CopyFrom(data)}).Wait();
    }

    Socket socket = null;

    public static bool ReceiveAll(Socket s, ref byte[] a){
      int i = 0;
      int k;
      do {
        k = s.Receive(a, i, a.Length-i, SocketFlags.None);
        i += k;
      } while (i < a.Length && k > 0);

      return k != 0; // 0 bytes received indicates socket failure
    }

    public static byte[] Receive(Socket s, int n){
      var res = new byte[n];
      var success = ReceiveAll(s, ref res);
      if(!success)
        throw new Exception("Something went wrong...");
      return res;
    }

    public static bool is_connected(Socket socket){
      // https://stackoverflow.com/questions/2661764/how-to-check-if-a-socket-is-connected-disconnected-in-c
      return !(socket.Poll(1, SelectMode.SelectRead) && socket.Available == 0);
    }

    // public IEnumerator ConnectionLoop(){
    //   while(true){
    //     var hostStringOrNull = System.Environment.GetEnvironmentVariable("UNITON_HOST");
    //     var hostString = String.IsNullOrEmpty(hostStringOrNull) ? "127.0.0.1" : hostStringOrNull;
    //     var host = IPAddress.Parse(hostString);

    //     var portStringOrNull = System.Environment.GetEnvironmentVariable("UNITON_PORT");
    //     var portString = String.IsNullOrEmpty(portStringOrNull) ? "11000" : portStringOrNull;
    //     var port = Int32.Parse(portString);

    //     IPEndPoint localEndPoint = new IPEndPoint(host, port); 
    //     Socket listener_socket = new Socket(host.AddressFamily, SocketType.Stream, ProtocolType.Tcp);  
    //     listener_socket.SetSocketOption(SocketOptionLevel.Socket, SocketOptionName.ReuseAddress, 1);

    //     // Bind the socket to the local endpoint and  listen for incoming connections.
    //     Thread.Sleep(1100);
    //     Debug.Log("Bind");
    //     listener_socket.Bind(localEndPoint);  
    //     listener_socket.Listen(10);  // argument is the max number of pending connections


    //     // Start listening for connections.
    //     cmd_stream_closed = true;

    //     Log.Print("Uniton waiting for a connection...");  
    //     // Program is suspended while waiting for an incoming connection.
        
    //     var listen = Task<Socket>.Run(() => {return listener_socket.Accept();});
    //     while(!listen.IsCompleted) yield return null;
    //     Socket socket = listen.Result;

    //     try{
          
    //       this.socket = socket; // needed to send in FixedUpdate
    //       // Don't allow another socket to bind to this port.
    //       // handler.ExclusiveAddressUse = true;

    //       // The socket will linger for 10 seconds after Socket.Close is called.
    //       // handler.LingerState = new LingerOption (true, 10);

    //       // Disable the Nagle Algorithm for this tcp socket.
    //       socket.NoDelay = true;

    //       // Set the receive buffer size to 8k
    //       // handler.ReceiveBufferSize = 8192;

    //       // Set the timeout for synchronous receive methods to 1 second (1000 milliseconds.)
    //       socket.ReceiveTimeout = 1000;

    //       // Set the send buffer size to 8k.
    //       // handler.SendBufferSize = 8192;

    //       // Set the timeout for synchronous send methods to 1 second (1000 milliseconds.)			
    //       socket.SendTimeout = 1000;

    //       if(!Handshake(socket))
    //         continue;

    //       var cl = CommandLoop(socket);

    //       while(true){
    //         try {
    //           var more = cl.MoveNext();
    //           if(!more)
    //             break;
    //         } finally {
    //           // we need to do this because try catch isn't allowed to contain yield
    //           socket.Close();
    //           this.socket = null;  
    //         }

    //         yield return null;
    //       }
        
    //       socket.Shutdown(SocketShutdown.Both); 

    //     } finally {
    //       socket.Close();
    //       this.socket = null;  
    //     }
    //   }
    // }

    // public static bool Handshake(Socket socket){
    //   // magic exchange
    //   var magic_number = BitConverter.ToInt32(Receive(socket, 4), 0);
    //   if(magic_number != Protocol.MAGIC_NUMBER)
    //     return false;  // TODO: is this the correc thing to do?
    //   socket.Send(BitConverter.GetBytes(Protocol.MAGIC_NUMBER));
    //   socket.Send(BitConverter.GetBytes(0));  // tell the client that bootstrapping is already

    //   // send version
    //   var v = Protocol.UNITON_VERSION.Split(".".ToCharArray()).Select(x => Int32.Parse(x)).ToArray();
    //   socket.Send(BitConverter.GetBytes(v[0]));
    //   socket.Send(BitConverter.GetBytes(v[1]));
    //   socket.Send(BitConverter.GetBytes(v[2]));


    //   // check sponsorship
    //   string errorMsg = "";
    //   if(Application.isEditor){
    //     // TODO: do checks here too
    //   } else {
    //     try {
    //       Type BI = GetTypeByFullName("Uniton.Bootstrap.BuildInfo");
    //       int contrib = (int) BI.GetProperty("contrib", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(null);
    //       string deviceId = (string) BI.GetProperty("deviceId", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(null);
    //       // TODO: lift to protocol
    //       if(contrib == 0){
    //         // Debug.Log("Building with Uniton Free");
    //         if(deviceId != SystemInfo.deviceUniqueIdentifier)
    //           errorMsg = "Error: Get Uniton Pro to run your apps on multiple devices!";
  
    //       } else if(contrib <= 500) {
    //         // Debug.Log("Building with Uniton Pro");
    //         // TODO: implement Uniton Pro check
    //       } else if(contrib <= 5000) {
    //         // Debug.Log("Building with Uniton Build");
    //       } else {
    //         // Debug.Log("Building with Uniton Build Pro");
    //       }
    //     } catch (Exception e) {
    //       errorMsg = "Error while checking version: \n\n" + e.ToString();
    //     }
    //   }

    //   socket.Send(BitConverter.GetBytes((int) errorMsg.Length));
    //   if(errorMsg.Length > 0)
    //     socket.Send(Encoding.UTF8.GetBytes(errorMsg));

    //   if(errorMsg.Length > 0){
    //     return false;  // same error is going to happen when the client reconnects in the next iteration, but this is better than just shutting the app down, no?
    //   }

    //   return true;
    // }


    // public IEnumerator CommandLoop(Socket socket){
    //   // init object storage
    //   sho = new List<object>();
    //   AddObject(0, typeof(Type));
    //   AddObject(1, this);
    //   // sho.Add(123);
    //   // sho.Add(this);

    //   byte[] msg_len_buffer = new byte[4];
      
    //   bool ok = true;
      
    //   while(ok){
    //     if(!is_connected(socket)) break;
    //     step_next = false;
        
    //     while(!step_next && socket.Available > 0){
    //       // get msg length
    //       ok = ReceiveAll(socket, ref msg_len_buffer);
    //       if(!ok) break;
    //       var msg_len = BitConverter.ToInt32(msg_len_buffer, 0);

    //       // get message
    //       byte[] msg_buffer = new byte[msg_len];
    //       ok = ReceiveAll(socket, ref msg_buffer);
    //       if(!ok) break;
          
    //       exec_cmd(msg_buffer);  // can set step_next

    //       if(stepping) socket.Poll(-1, SelectMode.SelectRead);  // block until socket.Available > 0
    //     }
    //     yield return null;
    //   }   
    // }


    public IEnumerator CmdStream(){

      // while(true){
      // var hostStringOrNull = System.Environment.GetEnvironmentVariable("UNITON_HOST");
      // var hostString = String.IsNullOrEmpty(hostStringOrNull) ? "127.0.0.1" : hostStringOrNull;
      // var host = IPAddress.Parse(hostString);

      // var portStringOrNull = System.Environment.GetEnvironmentVariable("UNITON_PORT");
      // var portString = String.IsNullOrEmpty(portStringOrNull) ? "11000" : portStringOrNull;
      // var port = Int32.Parse(portString);
      
      // IPEndPoint localEndPoint = new IPEndPoint(host, port); 
      // Socket listener_socket = new Socket(host.AddressFamily, SocketType.Stream, ProtocolType.Tcp);  
      // listener_socket.SetSocketOption(SocketOptionLevel.Socket, SocketOptionName.ReuseAddress, 1);

      // // Bind the socket to the local endpoint and  listen for incoming connections.  
      // Thread.Sleep(3000);  // this is critical otherwise we'll get "Adress already in use". I've all options to close the bootstrap socket immediately but nothing worked. So the only option is to wait.
      // // Debug.Log("Bind");
      // listener_socket.Bind(localEndPoint);  
      // listener_socket.Listen(1);  // argument is the max number of pending connections


      // Log.Print("Uniton waiting for a connection...");  
      // // Program is suspended while waiting for an incoming connection.
      
      // var listen = Task<Socket>.Run(() => {return listener_socket.Accept();});
      
      // while(!listen.IsCompleted) yield return null;
    
      // Socket socket = listen.Result;

      Type S = GetTypeByFullName("Uniton.Bootstrap.SocketBox");
      var socket = (Socket) S.GetField("socket").GetValue(null);
      try{ 

        // TODO: this is waaay too nested. modularize!

        this.socket = socket; // needed to send in FixedUpdate
        // Don't allow another socket to bind to this port.
        // handler.ExclusiveAddressUse = true;

        // The socket will linger for 10 seconds after Socket.Close is called.
        // handler.LingerState = new LingerOption (true, 10);

        // Disable the Nagle Algorithm for this tcp socket.
        socket.NoDelay = true;

        // Set the receive buffer size to 8k
        // handler.ReceiveBufferSize = 8192;

        // Set the timeout for synchronous receive methods to 1 second (1000 milliseconds.)
        socket.ReceiveTimeout = 1000;

        // Set the send buffer size to 8k.
        // handler.SendBufferSize = 8192;

        // Set the timeout for synchronous send methods to 1 second (1000 milliseconds.)			
        socket.SendTimeout = 1000;
        

        // handshake
        // var magic_number = BitConverter.ToInt32(Receive(socket, 4), 0);
        // if(magic_number != Protocol.MAGIC_NUMBER)
        //   continue;  // TODO: is this the correc thing to do?
        // socket.Send(BitConverter.GetBytes(Protocol.MAGIC_NUMBER));
        // socket.Send(BitConverter.GetBytes(0));  // tell the client that bootstrapping is already

        // send version
        var v = Protocol.UNITON_VERSION.Split(".".ToCharArray()).Select(x => Int32.Parse(x)).ToArray();
        socket.Send(BitConverter.GetBytes(v[0]));
        socket.Send(BitConverter.GetBytes(v[1]));
        socket.Send(BitConverter.GetBytes(v[2]));


        // check sponsorship
        string errorMsg = "";
        if(Application.isEditor){
          // TODO: do checks here too
        } else {
          try {
            Type BI = GetTypeByFullName("Uniton.Bootstrap.BuildInfo");
            int contrib = (int) BI.GetField("contrib").GetValue(null);
            string deviceId = (string) BI.GetField("deviceId").GetValue(null);
            // TODO: lift to protocol
            if(contrib == 0){
              // Debug.Log("Building with Uniton Free");
              if(deviceId != SystemInfo.deviceUniqueIdentifier)
                errorMsg = "Error: Please get Uniton Pro to run on multiple devices";
    
            } else if(contrib <= 500) {
              // Debug.Log("Building with Uniton Pro");
              // TODO: implement Uniton Pro check
            } else if(contrib <= 5000) {
              // Debug.Log("Building with Uniton Build");
            } else {
              // Debug.Log("Building with Uniton Build Pro");
            }
          } catch (Exception e) {
            errorMsg = "Error while checking version: \n\n" + e.ToString();
          }
        }

        socket.Send(BitConverter.GetBytes((int) errorMsg.Length));
        if(errorMsg.Length > 0)
          socket.Send(Encoding.UTF8.GetBytes(errorMsg));

        if(errorMsg.Length > 0){
          throw new Exception(errorMsg);
          // continue;  // same error is going to happen when the client reconnects in the next iteration, but this is better than just shutting the app down, no?
        }

        
        // the main loop

        // init object storage
        sho = new List<object>();
        AddObject(0, typeof(Type));
        AddObject(1, this);
        // sho.Add(123);
        // sho.Add(this);


        // Start listening for connections.
        cmd_stream_closed = true;  // TODO: what's this?

        byte[] msg_len_buffer = new byte[4];
    
        bool ok = true;
        
        while(ok){
          if(!is_connected(socket)) break;
          step_next = false;
          
          while(!step_next && socket.Available > 0){
            // get msg length
            ok = ReceiveAll(socket, ref msg_len_buffer);
            if(!ok) break;
            var msg_len = BitConverter.ToInt32(msg_len_buffer, 0);

            // get message
            byte[] msg_buffer = new byte[msg_len];
            ok = ReceiveAll(socket, ref msg_buffer);
            if(!ok) break;
            
            exec_cmd(msg_buffer);  // can set step_next

            if(stepping) socket.Poll(-1, SelectMode.SelectRead);  // block until socket.Available > 0
          }
          yield return null;

        }

        // Log.Print("Shutting down socket");
        // socket.Shutdown(SocketShutdown.Both);  // doesn't seem to do any good


      } finally {
        // socket.Close();
        // Debug.Log("Closing Uniton connection");
        this.socket = null;

        // TODO: move the following lines to protocol
        // Type S = GetTypeByFullName("Uniton.Bootstrap.SocketBox");
        S.GetField("isStale").SetValue(null, true);  // mark socket as stale, reload everything

        GameObject.Destroy(this.gameObject);  
      }

      //   break;  // let bootstrap handle reconnect, remove this loop..
      // }
    } 

    // like python bound method
    struct BoundMethod {
      public Type t;
      public MethodInfo[] candidate_methods;  // methods with the same name but different signatures (argument number and types)
      public object obj;
      public BindingFlags flags;
    }

    // like python getattr
    // not able to find extension methods
    // https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/extension-methods
    // to find extension methods we'd have to iterate all classes and look for them
    // https://stackoverflow.com/questions/299515/reflection-to-identify-extension-methods
    // TODO: this is returning invalid members if obj a Type!
    // TODO: some members, e.g. this.updates  are missing!
    object GetMember(string name, object obj){
      // var a = ((IEnumerable<object>)args).ToArray();
      // var rid = (int) a[0];
      
      Log.Print("getmember " + name + " " + ToStr(obj), Log.Level.VERBOSE);

      MemberInfo[] infos = null;
      Type t = null;
      BindingFlags flags = BindingFlags.Public;  // init to dummy

      if (obj is Type){
        t = (Type) obj;
        flags = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.FlattenHierarchy;
        infos = t.GetMember(name, flags);
      }

      if (infos == null || infos.Length == 0){
        // if obj is a Type but method wasn't found
        // or if obj isn't a Type
        t = obj.GetType();
        flags = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.GetField | BindingFlags.GetProperty| BindingFlags.Static | BindingFlags.FlattenHierarchy;
        infos = t.GetMember(name, flags);
      }

      if (infos.Length == 0){
        // if we havent found anything yet look in interfaces (i.e. subclasses)
        // interfaces aren't covered by BindingFlags.FlattenHierarchy
        // https://stackoverflow.com/questions/358835/getproperties-to-return-all-properties-for-an-interface-inheritance-hierarchy

        flags = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.GetField | BindingFlags.GetProperty| BindingFlags.Static | BindingFlags.FlattenHierarchy;
        foreach(var itf in t.GetInterfaces()){
          infos = itf.GetMember(name, flags);
          if(infos.Length > 0)
            break;
        }
      }
      object ret = null;

      if (infos != null && infos.Length > 0){
        var mt = infos[0].MemberType;
        if(mt == MemberTypes.Method){
          ret = new BoundMethod {t=t, candidate_methods=infos.Cast<MethodInfo>().ToArray(), obj=obj, flags=flags};
        } else if (mt == MemberTypes.Field) {
          ret = ((FieldInfo) infos[0]).GetValue(obj);  // TODO: check len infos ?
        } else if (mt == MemberTypes.Property) {
          ret = ((PropertyInfo) infos[0]).GetMethod.Invoke(obj, null);
        }
      }
      else
        throw new System.ArgumentException("Invalid Member " + name + " for object " + obj);

      // return AddObject(rid, ret);
      return ret;

    } 

    void SetMember(object obj, string name, object[] value){
      Log.Print("SetMember " + ToStr(obj) + " " + ToStr(name) + " " + ToStr(value), Log.Level.VERBOSE);

      Type t;
      BindingFlags flags;

      if (obj is Type){
        t = (Type) obj;
        flags = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.FlattenHierarchy;
      } else {
        t = obj.GetType();
        flags = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Static | BindingFlags.FlattenHierarchy;
      }

      flags = flags | BindingFlags.SetProperty | BindingFlags.SetField;
      t.InvokeMember(name, flags, Type.DefaultBinder, obj, value);
    }

    T[] ArrayCopy<T>(T[] x, int a, int b){
      var len = b - a;
      var r = new T[len];
      Array.Copy(x, a, r, 0, len);
      return r;
    }

    object[] ArrayCopy(object[] x, int a){
      return ArrayCopy(x, a, x.Length);
    }
    static T[] Concat<T>(T[] x, T[] y){
      var z = new T[x.Length + y.Length];
      x.CopyTo(z, 0);
      y.CopyTo(z, x.Length);
      return z;
    }

    
    object Invoke(object callable, object[] args){
      // like python call

      Log.Print("invoke " + ToStr(callable) + " " + ToStr(args), Log.Level.VERBOSE);
      object ret = null;

      try{
        if (callable is BoundMethod){
          var mi = (BoundMethod) callable;
          object state;
          var m = Type.DefaultBinder.BindToMethod(mi.flags, mi.candidate_methods, ref args, null, null, null, out state);
          ret = m.Invoke(mi.obj, mi.flags, null, args, null);
        }
        else if (callable is MethodInfo){
          Log.Print("" + args);
          var m = (MethodInfo) callable;
          var obj = args[0];
          var args_ = ArrayCopy(args, 1);
          ret = m.Invoke(obj, args_);
        }
        else if (callable is Type){
          // https://docs.microsoft.com/en-us/dotnet/api/system.activator.createinstance?view=netframework-4.7.2#System_Activator_CreateInstance_System_Type_System_Object___
          ret = Activator.CreateInstance((Type) callable, args);
        }
        else
          throw new System.ArgumentException("Object " + ToStr(callable) + " can't be called");

      }
      catch (MissingMethodException){
        throw new System.ArgumentException(ToStr(callable) + " could not be called with arguments: " + string.Join(", ", args.Select(a => ToStr(a))));
      }

      // return AddObject(rid, ret);
      return ret;
    }

    // public int cid = 0;
    // public object cobj;
    
    object GetObject(int id){
      // if (cid == id) return cobj;
      // else return sho[id];
      return sho[id];
    }
    // void AddObject(int rid, object v){
    //   if (rid == cid)
    //     cobj = v;
    //   else {
    //     AddObjectSlow(cid, cobj);
    //     cid = rid;
    //     cobj = v;
    //   }
    // }
    void AddObject(int rid, object v){
      // omap[rid] = v;
      if(sho.Count == rid){
        sho.Add(v);
        // Debug.Log("Added " + v + " at " + rid + " = " + sho[rid]);
      }
      else {
        sho[rid] = v;
        // Debug.Log("Added " + v + " at " + rid + " = " + sho[rid]);
      }
    }


    // Util methods:

    public void setStepping(bool x){
      stepping = x;
    }

    public void step() {
      step_next = true;
    }

    public static int empty_test(){
      return 3;
    }
    public static int test(int x){
      return 3 * x;
    }

    public int best(int x){
      return 3 * x;
    }

    public string aga = "fjyea";

    class AttributeError : Exception {
      // TODO: use this in Get/SetMembers
      public AttributeError(object x, string key)
          : base("'" + x.GetType() + "' object has no attribute '" + key + "'"){

      }
    }

    int pathDepth(string s, char delimiter='.'){
      // normally string split could be used for this
      // for some reason string split doesn't return an empty list for a empty string though
      return s == "" ? 0 : s.Count(c => c == delimiter) + 1;
    }

    public string[] GetNamespaces(string parentNamespace=""){
      int parentDepth = pathDepth(parentNamespace);
      return System.AppDomain.CurrentDomain.GetAssemblies()
        .SelectMany(asm => asm.GetTypes())
        .Select(t => t.Namespace == null ? "" : t.Namespace)  // global namespace is represented by null
        .Distinct()
        .Where(ns => ns.StartsWith(parentNamespace))
        .Where(ns => pathDepth(ns) == parentDepth + 1)
        .ToArray();
    }


    public IEnumerable<Type> GetTypesInNamespace(string ns){
      ns = (ns == "" ? null : ns); // global namespace is represented by null
      return System.AppDomain.CurrentDomain.GetAssemblies()
        .SelectMany(asm => asm.GetTypes())
        .Where(t => t.Namespace == ns);
    }

    public string[] GetTypenamesInNamespace(string ns=""){
      return GetTypesInNamespace(ns).Select(t => t.FullName).ToArray();
    }

    public static Type GetTypeByFullName(string n){
      return System.AppDomain.CurrentDomain.GetAssemblies()
        .SelectMany(asm => asm.GetTypes())
        .First(t => t.FullName == n);
    }

    public Type[] SubclassesOf(Type type){
      return System.AppDomain.CurrentDomain.GetAssemblies()
        .SelectMany(asm => asm.GetTypes())
        .Where(t => t.IsSubclassOf(type))
        .ToArray();
    }

    // depreciated
    public Type GetTypeInNamespace(string name, string ns=""){
      // TODO: make similar method for struct, class, enum, delegate and interface?
      Type t = GetTypesInNamespace(ns).FirstOrDefault(t => t.Name == name);
      if(t == null)
        throw new Exception("Namespace '" + ns + "' has no type '" + name + "'");
      return t;
    }

    // depreciated
    public Type[] GetTypesBelowNamespace(string name, string ns=""){
      return System.AppDomain.CurrentDomain.GetAssemblies()
        .SelectMany(asm => asm.GetTypes())
        .Where(t => (t.Namespace == null ? "" : t.Namespace).StartsWith(ns)) // global namespace is represented by null
        .Where(t => t.Name == name)  // TODO: the Name attribute is flawed use FullName
        .ToArray();
    }

    // depreciated
    public String[] TypenamesBelowNamespace(string ns=""){
      return System.AppDomain.CurrentDomain.GetAssemblies()
        .SelectMany(asm => asm.GetTypes())
        .Where(t => (t.Namespace == null ? "" : t.Namespace).StartsWith(ns)) // global namespace is represented by null
        .Select(t => t.FullName)
        .ToArray();
    }

    static string ToStr(object x, int level=0) {
      if (x is IEnumerable<object>){
        var en = (IEnumerable<object>) x;
        var n = en.Count();
        if (n < 7)
          return "<" + x.GetType() + "> " +"{" + string.Join(", ", en.Select(e => ToStr(e, level+1))) + "}";
        else
          return "<" + x.GetType() + "> " +"{ ... " + n + " items ...}";
      }
      else if (x is BoundMethod){
        var en = ((BoundMethod) x).candidate_methods;
        return "<BoundMethod> {" + string.Join(", ", en.Select(e => ToStr(e, level+1))) + "}";
      }
      else if (x is Type){
        // display link to Unity documentation
        // links in terminal: https://gist.github.com/egmontkob/eb114294efbcd5adb1944c9f3cb5feda
        Type t = (x as Type);
        if ((new string[]{"UnityEngine", "Unity", "UnityEditor"}).Contains(t.Namespace)){
          // TODO: this doesn't work for UnityEngine.SceneManagement, etc.
          // TODO: this only works for core unity classes (the urls are kinda incosistent)
          return "<Type> \x1B]8;;https://docs.unity3d.com/Documentation/ScriptReference/" + t.Name + "\x1B\\" + t.FullName + "\x1B]8;;\x1B\\";
        } else if (false)
          return t.FullName;
        else
          return "<Type> " + t.FullName;
      }
      else if (x is string)
        return "\"" + (string)x + "\"";
      else if (x == null)
        return "null";
      else
        return x.ToString();
    }
  }

}