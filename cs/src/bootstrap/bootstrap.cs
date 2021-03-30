using System.Reflection;
using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System;
using System.Threading;
using System.Threading.Tasks;
using System.Linq;
using System.IO;
using System.Collections;
using System.Collections.Generic;


namespace Uniton.Bootstrap{
  public class Loader{
    [RuntimeInitializeOnLoadMethod]
    public static void OnLoad(){
      Debug.Log("Uniton is running!");

      AudioListener.volume = 0;  // disable sound

      var pausedString = System.Environment.GetEnvironmentVariable("UNITON_PAUSED");
      var paused = String.IsNullOrEmpty(pausedString) ? false : Convert.ToBoolean(pausedString);

      if(paused){
          Time.timeScale = 0;
      }

      // We add ourselves as a game object such that Start() gets called on the main thread
      GameObject go = new GameObject("UnitonBootstrap");
      go.AddComponent<BootstrapBehaviour>();
    }
  }

  public static class SocketBox{
    public static Socket socket;
    public static bool isStale = false;  // can be used to signal that the socket has been used up and can be closed
  }


  public class BootstrapBehaviour : MonoBehaviour{

    IEnumerator loadDllLoop;

    void Awake() {
      // Prevent being destroyed when the scene is unloaded https://docs.unity3d.com/ScriptReference/Object.DontDestroyOnLoad.html
      DontDestroyOnLoad(this.gameObject);
      
      // Coroutine to load Uniton's core.dll
      this.loadDllLoop = LoadDllLoop();
    }

    void Update(){
      loadDllLoop.MoveNext();
    }

    void OnDestroy() {
      ((IDisposable)this.loadDllLoop).Dispose();  // necessary for any finally blocks to be executed
    }

    IEnumerator LoadDllLoop(){
      var hostStringOrNull = System.Environment.GetEnvironmentVariable("UNITON_HOST");
      var hostString = String.IsNullOrEmpty(hostStringOrNull) ? "127.0.0.1" : hostStringOrNull;

      var portStringOrNull = System.Environment.GetEnvironmentVariable("UNITON_PORT");
      var portString = String.IsNullOrEmpty(portStringOrNull) ? "11000" : portStringOrNull;
      var port = Int32.Parse(portString);


      var host = IPAddress.Parse(hostString);
      IPEndPoint localEndPoint = new IPEndPoint(host, port);

      while(true){

        Socket listener_socket = new Socket(host.AddressFamily, SocketType.Stream, ProtocolType.Tcp);

        // Bind sometimes fails even though the socket was properly closed, therefore we set reuseaddress
        // https://hea-www.harvard.edu/~fine/Tech/addrinuse.html
        listener_socket.SetSocketOption(SocketOptionLevel.Socket, SocketOptionName.ReuseAddress, 1);

        for(var i=0;; i++){
          try{
            listener_socket.Bind(localEndPoint);
            break;
          } catch (SocketException) {
            // if time is less than 10s, wait and retry
            if(i<100)
              Thread.Sleep(100);  
            else
              throw;
          }
        }

        listener_socket.Listen(10);  // argument is the max number of pending connections
        
        Debug.Log("Listening for a new connection...");
        // Socket socket = await Task.Run(() => listener_socket.Accept());
        var listen = Task<Socket>.Run(() => {return listener_socket.Accept();});  // TODO: use blocking socket instead?
        while(!listen.IsCompleted) yield return null;
        Socket socket = listen.Result;
        SocketBox.socket = socket;
        SocketBox.isStale = false;

        try{
          socket.SetSocketOption(SocketOptionLevel.Socket, SocketOptionName.Linger, new LingerOption(true, 0));

          socket.ReceiveTimeout = 1000;
          socket.SendTimeout = 1000;
          

          try{
            LoadDll(socket);
          } catch (Exception e){
            Debug.Log(e);
          }

          while(!SocketBox.isStale)
            yield return null;

        } finally {
          // Debug.Log("Restart Bootstrap");
          socket.Close();
          // Thread.Sleep(2200);
        }
      }

      // TODO: the following is no longer true: After loading the core.dll we're done. Dlls can't be unloaded. Therefore, to load a new core.dll the application needs to be restarted.
      GameObject.Destroy(this.gameObject);  
    }

    static Type UnitonLoader(){
      return System.AppDomain.CurrentDomain.GetAssemblies()
        .SelectMany(asm => asm.GetTypes())
        .FirstOrDefault(t => t.FullName == "Uniton.Loader");
    }

    private static void LoadDll(Socket socket){
      // magic exchange
      var magic_number = BitConverter.ToInt32(Receive(socket, 4), 0);
      if(magic_number != Protocol.MAGIC_NUMBER)
        throw new Exception("Handshake failed");

      socket.Send(BitConverter.GetBytes(Protocol.MAGIC_NUMBER));
      // socket.Send(BitConverter.GetBytes(1));  // signals that bootstrapping is necessary

      // receive dll data
      var msg_len = BitConverter.ToInt32(Receive(socket, 4), 0);
      var data = Receive(socket, msg_len);
      
      // remove "obfuscation"
      data = data.Skip(239).ToArray(); 
    
      // load
      if(UnitonLoader() == null){
        var assembly = Assembly.Load(data);
        // Debug.Log("LOADED!");
        // assembly.GetTypes().ToList().ForEach(t => Debug.Log(t.FullName));
        // var Loader = assembly.GetTypes().First(t => t.FullName == "Uniton.Loader");
        Debug.Log("Connected");
      } else {
        // Debug.Log("Skipping bootstrap since Uniton has already been loaded. If you experience unexpected behaviour, try restarting the process.");
        Debug.Log("Reconnected");
      }
      
      var Loader = UnitonLoader();
    
      Loader.GetMethod("OnLoad").Invoke(Loader, new object[] {});

      // Debug.Log("Send confirm");
      // socket.Send(BitConverter.GetBytes(0));  // confirmation
    }

    private static byte[] Receive(Socket s, int n){
      int i = 0;
      int k;
      var a = new byte[n];
      do {
        k = s.Receive(a, i, a.Length-i, SocketFlags.None);
        i += k;
      } while (i < n && k > 0);

      if(k == 0) // 0 bytes received indicates socket failure
        throw new Exception("Something went wrong...");
      
      return a;
    }
  }

}
