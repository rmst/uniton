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

using Pysharp;

// using UnityEditor;  // needed for [InitializeOnLoad]
// [InitializeOnLoad]
// public class ETest{
//   static ETest(){
//     Debug.Log("Running in the Editor!");
//   }
// }


public class UnityBehaviour : MonoBehaviour {

  [RuntimeInitializeOnLoadMethod]
  public static void OnLoad(){
    Log.Print("Pysharp is running", Log.Level.INFO);
    GameObject go = new GameObject("Pysharp");
    go.AddComponent<UnityBehaviour>();
  }

  // const int Port = 50051;
  // Dispatcher disp;
  Connection service;
  // Use this for initialization
  void Start () {


    // disp = new Dispatcher();
    service = new Connection();
    // service.disp = disp;
    service.Init();

    // service.ShareObj(typeof(MethodInfo).GetMethod("Invoke", new [] {typeof(object), typeof(object[])}));

    // service.ShareObj(typeof(Type).GetMethod("GetMethod", new [] {typeof(string), typeof(Type[])}));

    // service.ShareObj(typeof(Type).GetMethod("InvokeMember", new [] {typeof(string), typeof(BindingFlags), typeof(Binder), typeof(object), typeof(object[])}));

    // service.ShareObj(typeof(object).GetMethod("GetType"));
    // service.ShareObj(this);
    // service.ShareObj(typeof(rpctest).GetMethod("GetGlobalType"));

    // Server server = new Server {
    //     Services = { UnpyGrpcService.BindService(service) },
    //     Ports = { new ServerPort("0.0.0.0", Port, ServerCredentials.Insecure) }
    // };
  
    // server.Start();

    // https://docs.unity3d.com/ScriptReference/MonoBehaviour.StartCoroutine.html
    // StartCoroutine(service.CaptureFrames); 
  }

  void Awake() {
    // https://docs.unity3d.com/ScriptReference/Object.DontDestroyOnLoad.html
    DontDestroyOnLoad(this.gameObject);
  }

  // Update is called once per frame
  void Update () {
    // disp.Update();
    service.Update();
  }

  void FixedUpdate(){
    service.FixedUpdate();
  }

  void OnGUI(){
    service.OnGUI();
  }

}