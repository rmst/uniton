using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

// using UnpyGrpc;
using System.Threading.Tasks;
// using Grpc.Core;
using System.Runtime.CompilerServices;
using System.Reflection;
using System.Linq;
using System;

using System;  
using System.Net;  
using System.Net.Sockets;  
using System.Text; 
using System.Threading.Tasks;

using Microsoft.CSharp;
using System.CodeDom.Compiler;


namespace Uniton{

  // this is the entry point for the bootstrap process
  public static class Loader {
    public static void OnLoad(){
      GameObject go = new GameObject("Uniton");
      go.AddComponent<Connection>();
    }
  }

  // public class UnityBehaviour : MonoBehaviour {

  //   // [RuntimeInitializeOnLoadMethod]
  //   public static void OnLoad(){
  //     // Log.Print("Uniton " + Flavor.name + "  " + Protocol.UNITON_VERSION + " is running", Log.Level.INFO);

  //     AudioListener.volume = 0;  // disable sound

  //     GameObject go = new GameObject("Uniton");
  //     go.AddComponent<UnityBehaviour>();
  //   }

  //   Connection service;
  //   // Use this for initialization

  //   void Awake() {
  //     this.service = new Connection();
  //     // https://docs.unity3d.com/ScriptReference/Object.DontDestroyOnLoad.html
  //     DontDestroyOnLoad(this.gameObject);
  //   }

  //   void OnDestroy() {
  //     this.service.Dispose();
  //   }

  //   // Update is called once per frame
  //   void Update () {
  //     this.service.Update();
  //   }

  //   void FixedUpdate(){
  //     this.service.FixedUpdate();
  //   }

  //   void OnGUI(){
  //     this.service.OnGUI();
  //   }

  // }

}