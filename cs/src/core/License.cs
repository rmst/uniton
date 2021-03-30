
using System.IO;
using System.Linq;
using System;
using System.Net.Http;
using System.Text;
// using System.Net.Http.Headers;
using System.Security.Cryptography;

using UnityEngine;


// class TestClass
// {
//     static void Main(string[] args)
//     {
//         // Display the number of command line arguments.
//         Console.WriteLine(args.Length);
//     }
// }


// namespace Uniton{
//   class LicenseUtil{
//     public static string EnvVar(string name, string alt=null){
//       var v = System.Environment.GetEnvironmentVariable(name);
//       if(String.IsNullOrEmpty(v)){
//         if(alt != null)
//           return alt;
//         else
//           throw new Exception($"Environment variable '{name}' does not exist.");
//       } else {
//         return v;
//       }
//     }
    
//     public static string UserDataDir(){
//       if(Application.platform == RuntimePlatform.WindowsEditor){
//         return Util.EnvVar("CSIDL_APPDATA");
//       } else if(Application.platform == RuntimePlatform.OSXEditor){
//         var home = Util.EnvVar("HOME");
//         return $"{home}/Library/Application Support/";
//       } else if(Application.platform == RuntimePlatform.LinuxEditor) {
//         var home = Util.EnvVar("HOME");
//         return Util.EnvVar("XDG_DATA_HOME", $"{home}/.local/share");
//       } else {
//         throw new Exception("Unsupported platform");
//       }
//     }
//     public static void Check(dynamic buildInfo){
//       var udd = LicenseUtil.UserDataDir();
//       var tokenPath = Path.Combine(udd, "Uniton", "token");
//       if(File.Exists(tokenPath)){
//         try{
//           var token = File.ReadAllText(tokenPath);
//           tokenHash = SHA256.Create()
//             .ComputeHash(Encoding.UTF8.GetBytes(token))
//             .Select(b => b.ToString("x2")) // convert bytes to strings
//             .Aggregate(string.Concat);  // concatenate everything

//         } catch (Exception e) {
//           Debug.Log($"Could not verify Uniton sponsorship. Check: \n\n {e}");
//         }
//       }
//     }
//   }
// }