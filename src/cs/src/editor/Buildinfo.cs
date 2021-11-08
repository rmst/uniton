// #if UNITY_EDITOR
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEditor.Compilation;
using UnityEditor.Callbacks;

using UnityEngine;

using System.IO;
using System.Linq;
using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Collections.Generic;
using System.Security.Cryptography;



namespace Uniton.Editor{

  [InitializeOnLoad]
  public class Startup {
    static Startup(){
      var dllpath = (new Uri(System.Reflection.Assembly.GetExecutingAssembly().CodeBase)).LocalPath;
      
      var dllDir = Path.GetDirectoryName(dllpath);
      if((new DirectoryInfo(dllDir)).Name != "Editor"){
        // Editor directories have a special purpose in Unity
        // .cs and .dll in there will only be executed in the Editor
        // this is important for us since we have some editor-only code
        
        var unitonDir = Path.Combine(dllDir, "Uniton");
        Directory.CreateDirectory(unitonDir);  // fine if exists

        var editorDir = Path.Combine(unitonDir, "Editor");
        Directory.CreateDirectory(editorDir);  // fine if exists

        File.Move(dllpath, Path.Combine(editorDir, "editor.dll"));
        File.Delete(dllpath + ".meta");

        var fileStream = File.Create(Path.Combine(unitonDir, "bootstrap.dll"));
        var dllstream = System.Reflection.Assembly.GetExecutingAssembly().GetManifestResourceStream("bootstrap.dll");
        dllstream.Seek(0, SeekOrigin.Begin);
        dllstream.CopyTo(fileStream);
        fileStream.Close();

        AssetDatabase.Refresh(ImportAssetOptions.ForceUpdate);
      }
    }
  }

  [System.Serializable]
  public class ProductInfo {
      public string title;
  }

  [System.Serializable]
  public class RootObject {
      public ProductInfo product_info;
  }

  public static class Util {
    public static string EnvVar(string name, string alt=null){
      var v = System.Environment.GetEnvironmentVariable(name);
      if(String.IsNullOrEmpty(v)){
        if(alt != null)
          return alt;
        else
          throw new Exception($"Environment variable '{name}' does not exist.");
      } else {
        return v;
      }
    }

    public static Dictionary<string, string> parseQuery(string q){
        return q
          .Split("&".ToCharArray())
          .Select(x=> x.Split("=".ToCharArray()))
          .ToDictionary(x => Uri.UnescapeDataString(x[0]), x => Uri.UnescapeDataString(x[1]));  
    }

    // public static string ubi = Path.Combine("Assets", "Resources", "ubi.cs");  // uniton build info file

    public static string UserDataDir(){
      if(Application.platform == RuntimePlatform.WindowsEditor){
        return Util.EnvVar("CSIDL_APPDATA");
      } else if(Application.platform == RuntimePlatform.OSXEditor){
        var home = Util.EnvVar("HOME");
        return $"{home}/Library/Application Support/";
      } else if(Application.platform == RuntimePlatform.LinuxEditor) {
        var home = Util.EnvVar("HOME");
        return Util.EnvVar("XDG_DATA_HOME", $"{home}/.local/share");
      } else {
        throw new Exception("Unsupported platform");
      }
    }



    // TODO: Unused
    public static void SymmetricEncrypt(){
        byte[] key = { 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16 };

        try
        {
            //Create a file stream
            FileStream myStream = new FileStream("TestData.txt", FileMode.OpenOrCreate);

            //Create a new instance of the default Aes implementation class  
            // and configure encryption key.  
            Aes aes = Aes.Create();
            aes.Key = key;

            //Stores IV at the beginning of the file.
            //This information will be used for decryption.
            byte[] iv = aes.IV;
            myStream.Write(iv, 0, iv.Length);

            //Create a CryptoStream, pass it the FileStream, and encrypt
            //it with the Aes class.  
            CryptoStream cryptStream = new CryptoStream(
                myStream, 
                aes.CreateEncryptor(),
                CryptoStreamMode.Write);

            //Create a StreamWriter for easy writing to the
            //file stream.  
            StreamWriter sWriter = new StreamWriter(cryptStream);

            //Write to the stream.  
            sWriter.WriteLine("Hello World!");

            //Inform the user that the message was written  
            //to the stream.  
            Console.WriteLine("The file was encrypted.");
        }
        catch
        {
            //Inform the user that an exception was raised.  
            Console.WriteLine("The encryption failed.");
            throw;
        }
    }

  }

  
  [Serializable]
  public class SponsorQuery {
    public string query;
  }
  
  // necessary for json parse :D
  [Serializable]
  public class SponsorResult {
    [Serializable]
    public class Data{
      [Serializable]
      public class User {
        [Serializable]
        public class Sponsorship {
          [Serializable]
          public class Tier {
            public int monthlyPriceInCents;
          }
          public Tier tier;
        }
        public Sponsorship sponsorshipForViewerAsSponsor;
      }
      public User user;

      [Serializable]
      public class Viewer {
        public string name;
        public string login;
      }
      public Viewer viewer;
    }
    public Data data;
  }

  public static class Util2 {
    public static SponsorResult.Data Sponsor(string token){
      var c = new HttpClient();
      c.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
      c.DefaultRequestHeaders.UserAgent.Add(new ProductInfoHeaderValue("Uniton", "0.3.0"));  // TODO: use version variable
      var query = @"
        {
          user(login: ""uniton-dev""){
            sponsorshipForViewerAsSponsor{
              tier {
                monthlyPriceInCents
              }
            }
          }
          viewer {
            name
            login
          }
        }";

      // var jq = $"{{\"query\": \"{query}\"}}";
      // Debug.Log(jq);
      var res = c.PostAsync("https://api.github.com/graphql", new StringContent(JsonUtility.ToJson(new SponsorQuery {query=query}), Encoding.UTF8, "application/json"))
        .Result.Content.ReadAsStringAsync().Result;
      
      // Debug.Log(res);

      var sr = JsonUtility.FromJson<SponsorResult>(res);
      // Debug.Log($"{sr.data.user.sponsorshipForViewerAsSponsor.tier.monthlyPriceInCents}");
      return sr.data;
    }
  }

  public class GUI{
    private static readonly HttpClient client = new HttpClient();

    // https://docs.unity3d.com/ScriptReference/MenuItem.html
    [MenuItem("Uniton/Sign In with Github")]  
    static void SignInWizard(){
      try {
        string json = "{\"client_id\": \"8b9263c9919eea0291f4\", \"scope\": \"read:user\"}";
        // client.DefaultRequestHeaders.Accept.Add(
        // new MediaTypeWithQualityHeaderValue("application/json"));
        var content = new StringContent(json, Encoding.UTF8, "application/json");
        var response = client.PostAsync("https://github.com/login/device/code", content).Result;
        var c = response.Content.ReadAsStringAsync().Result;
        var j = Util.parseQuery(c);
        var uri = j["verification_uri"];
        var code = j["user_code"];
        var dcode = j["device_code"];
        // Debug.Log(j["device_code"]);
        if(EditorUtility.DisplayDialog("Sign in with Github", $"Please copy the copy the code: \n {code} \n and go to {uri}", "Open Link", "Cancel"))
          Application.OpenURL(uri);
        else
          return;

        if(!EditorUtility.DisplayDialog("Sign in with Github", $"Please copy the copy the code: \n {code} \n and go to {uri}", "Continue", "Cancel"))
          return;

        var response2 = client.PostAsync(
          "https://github.com/login/oauth/access_token", 
          new StringContent($"{{\"client_id\": \"8b9263c9919eea0291f4\", \"device_code\": \"{dcode}\", \"grant_type\": \"urn:ietf:params:oauth:grant-type:device_code\"}}", Encoding.UTF8, "application/json")
        ).Result;
        var res = Util.parseQuery(response2.Content.ReadAsStringAsync().Result);
        // Debug.Log(res["access_token"]);

        var dd = Path.Combine(Util.UserDataDir(), "Uniton");
        Directory.CreateDirectory(dd);  // fine if exists

        var token = res["access_token"];
        File.WriteAllText(Path.Combine(dd, "token"), token); 

        var d = Util2.Sponsor(token);
        if(d.user.sponsorshipForViewerAsSponsor == null){
          var go = EditorUtility.DisplayDialog("Not a sponsor", $"Hey {d.viewer.name}, you don't seem to be a Uniton sponsor. You can go to https://github.com/sponsors/uniton-dev to become one.", "Let's Go!", "Cancel");
          if(go)
            Application.OpenURL("https://github.com/sponsors/uniton-dev");
        } else {
          EditorUtility.DisplayDialog("Sign-in successful!", $"Hey {d.viewer.name},\nLet's build something great with Uniton!", "Cool!", "Ok");
        }
        
      } catch (Exception){
        if(EditorUtility.DisplayDialog("Sign-in failed", $"You can report this at https://github.com/uniton-dev/uniton/issues", "Report!", "Cancel"))
          Application.OpenURL("https://github.com/uniton-dev/uniton/issues");
      }
    }

    [MenuItem("Uniton/Delete Data")]  
    static void DeleteDataWizard(){
      var dd = Path.Combine(Util.UserDataDir(), "Uniton");
      Directory.Delete(dd, true);
    }
  }


  class OnPreprocessBuildClass : IPreprocessBuildWithReport{
  
    public int callbackOrder { get { return 0; } }

    public void OnPreprocessBuild(BuildReport report){
          
      int contrib = 0;
      string ghLogin = null;
      string tokenHash = null;

      var udd = Util.UserDataDir();
      var tokenPath = Path.Combine(udd, "Uniton", "token");
      if(File.Exists(tokenPath)){
        try{
          var token = File.ReadAllText(tokenPath);

          // TODO: lift to protocol
          tokenHash = SHA256.Create()
            .ComputeHash(Encoding.UTF8.GetBytes(token))
            .Select(b => b.ToString("x2")) // convert bytes to strings
            .Aggregate(string.Concat);  // concatenate everything

          var d = Util2.Sponsor(token);
          ghLogin = d.viewer.login;
          contrib = d.user.sponsorshipForViewerAsSponsor.tier.monthlyPriceInCents;

          if(ghLogin == "rmst"){
            contrib = 100000000;
          }

        } catch (Exception e) {
          Debug.Log($"Could not verify Uniton sponsorship. Check: \n\n {e}");
        }
      }

      // TODO: lift to protocol
      if(contrib == 0)
        Debug.Log("Building with Uniton Free");
      else if(contrib <= 500)
        Debug.Log("Building with Uniton Pro");
      else if(contrib <= 5000)
        Debug.Log("Building with Uniton Build");
      else
        Debug.Log("Building with Uniton Build Pro");

      var date = DateTime.Now.ToString("yyyy-MM-dd");

      // Directory.CreateDirectory("Assets/Resources");
      var dllpath = (new Uri(System.Reflection.Assembly.GetExecutingAssembly().CodeBase)).LocalPath;
      var unitonDir = Path.GetDirectoryName(Path.GetDirectoryName(dllpath));

      File.WriteAllText(unitonDir + ".bi.cs", $"namespace Uniton.Bootstrap{{public static class BuildInfo{{public const string date=\"{date}\"; public const string deviceId=\"{SystemInfo.deviceUniqueIdentifier}\"; public const string userId=\"{UnityEditor.CloudProjectSettings.userId}\"; public const string ghLogin=\"{ghLogin}\"; public const int contrib={contrib}; public const string tokenHash=\"{tokenHash}\"; }}}}");

      // var dllpath = (new Uri(System.Reflection.Assembly.GetExecutingAssembly().CodeBase)).LocalPath;  // TODO: what happens if building from source?

      // var fileStream = File.Create(dllpath + ".bootstrap.dll");
      // var dllstream = System.Reflection.Assembly.GetExecutingAssembly().GetManifestResourceStream("bootstrap.dll");
      // dllstream.Seek(0, SeekOrigin.Begin);
      // dllstream.CopyTo(fileStream);
      // fileStream.Close();
      
      // File.Move(dllpath, dllpath + ".backup");
      // File.Move(dllpath + ".backup.meta");

      AssetDatabase.Refresh(ImportAssetOptions.ForceUpdate);
    }

    [PostProcessBuildAttribute(0)]
    public static void OnPostprocessBuild(BuildTarget target, string pathToBuiltProject) {
      // Debug.Log( pathToBuiltProject );
      

      var dllpath = (new Uri(System.Reflection.Assembly.GetExecutingAssembly().CodeBase)).LocalPath;
      var unitonDir = Path.GetDirectoryName(Path.GetDirectoryName(dllpath));

      File.Delete(unitonDir + ".bi.cs");
      File.Delete(unitonDir + ".bi.cs.meta");

      // File.Delete(dllpath + ".bootstrap.dll");
      // File.Delete(dllpath + ".bootstrap.dll.meta");

      // File.Move(dllpath + ".backup", dllpath);
      // File.Move(dllpath + ".backup.meta", dllpath + ".meta");

      AssetDatabase.Refresh(ImportAssetOptions.ForceUpdate);
    }

  }


  [InitializeOnLoad]
  class NoErrorsValidator
  {

    static NoErrorsValidator() 
    {
      // if (Application.isBatchMode)
      CompilationPipeline.assemblyCompilationFinished += OnCompilationFinished;
    }
      
    private static void OnCompilationFinished(string s, CompilerMessage[] compilerMessages)
    {
        if (compilerMessages.Count(m => m.type == CompilerMessageType.Error) > 0){
          // EditorApplication.Exit(-1);

          var dllpath = (new Uri(System.Reflection.Assembly.GetExecutingAssembly().CodeBase)).LocalPath;
          var unitonDir = Path.GetDirectoryName(Path.GetDirectoryName(dllpath));

          File.Delete(unitonDir + ".bi.cs");
          File.Delete(unitonDir + ".bi.cs.meta");

          // File.Move(dllpath + ".backup", dllpath);
          // File.Move(dllpath + ".backup.meta", dllpath + ".meta");

          // File.Delete(dllpath + ".bootstrap.dll");
          // File.Delete(dllpath + ".bootstrap.dll.meta");
          AssetDatabase.Refresh(ImportAssetOptions.ForceUpdate);
        }
            
    }
  }
}
// #endif