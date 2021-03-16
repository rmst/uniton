using System.Reflection;
using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System;
using System.Threading;
using System.Threading.Tasks;
using System.Linq;


namespace Uniton{

  // using UnityEditor;  // needed for [InitializeOnLoad]
  // [InitializeOnLoad]
  // public class ETest{
  //   static ETest(){
  //     Debug.Log("Running in the Editor!");
  //   }
  // }


  public class Uniton {

    [RuntimeInitializeOnLoadMethod]
    public static void OnLoad(){
      // Log.Print("Uniton " + Flavor.name + "  " + Protocol.UNITON_VERSION + " is running", Log.Level.INFO);
      Debug.Log("Uniton Boostrap");
      AudioListener.volume = 0;  // disable sound

      // Task.Run(LoadDll);
      LoadDll();
    }

    static void LoadDll(){
      var hostStringOrNull = System.Environment.GetEnvironmentVariable("UNITONHOST");
      var hostString = String.IsNullOrEmpty(hostStringOrNull) ? "127.0.0.1" : hostStringOrNull;

      var portStringOrNull = System.Environment.GetEnvironmentVariable("UNITONPORT");
      var portString = String.IsNullOrEmpty(portStringOrNull) ? "11000" : portStringOrNull;
      var port = Int32.Parse(portString);

      // Assembly assembly = null;

      while(true){
        try{
          var data = LoadBytes(hostString, port);
          if(data != null){
            var assembly = Assembly.Load(data);
            Debug.Log("LOADED!");
            // assembly.GetTypes().ToList().ForEach(t => Debug.Log(t.FullName));
            dynamic ub = assembly.GetTypes().First(t => t.FullName == "Uniton.UnityBehaviour");
            // dynamic t = Type.GetType("Uniton.UnityBehaviour");
            // ub.OnLoad();
            ub.GetMethod("OnLoad").Invoke(ub, new object[] {});
            break;
          }
        } catch (Exception e){
          Debug.Log(e);
        }
        Thread.Sleep(500);  // 0.5s
      }
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

    // public static bool is_connected(Socket socket){
    //   // https://stackoverflow.com/questions/2661764/how-to-check-if-a-socket-is-connected-disconnected-in-c
    //   return !(socket.Poll(1, SelectMode.SelectRead) && socket.Available == 0);
    // }

    private static byte[] LoadBytes(string hostString, int port){
      // IPHostEntry ipHostInfo = Dns.GetHostEntry(Dns.GetHostName());  
      // IPAddress ipAddress = ipHostInfo.AddressList[0]; 


      var host = IPAddress.Parse(hostString);
      IPEndPoint localEndPoint = new IPEndPoint(host, port); 
      Socket listener = new Socket(host.AddressFamily, SocketType.Stream, ProtocolType.Tcp);  

      // Bind the socket to the local endpoint and   
      // listen for incoming connections.  
      listener.Bind(localEndPoint);  
      listener.Listen(10);  // argumetn is the max number of pending connections

      Debug.Log("Uniton waiting for a connection...");  
      // Program is suspended while waiting for an incoming connection.
      
      Socket handler = listener.Accept();
      // handler.NoDelay = true;
      handler.ReceiveTimeout = 1000;
      handler.SendTimeout = 1000;

      var magic_number = BitConverter.ToInt32(Receive(handler, 4), 0);
      if(magic_number != 1283621)
        return null;

      var msg_len = BitConverter.ToInt32(Receive(handler, 4), 0);
      var msg = Receive(handler, msg_len);

      Debug.Log("Shutting down socket");
      try{handler.Shutdown(SocketShutdown.Both);} catch(SocketException e) {Debug.Log(e);}
      try{handler.Close();} catch(SocketException e) {Debug.Log(e);}
      try{listener.Close();} catch(SocketException e) {Debug.Log(e);}
      return msg;
    }

    void OnGUI(){

    }

  }

}
