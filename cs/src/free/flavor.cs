using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEngine;
using UnityEditor.Build.Reporting;

using UnityEditor.SceneManagement; // will fail during compile of standalone
using System;

namespace Uniton{

    [InitializeOnLoad]  // will run as soon as the script is compiled
    public class FlavorGuard{
        static FlavorGuard(){
            BuildPlayerWindow.RegisterBuildPlayerHandler(BuildPlayerHandler);
        }

        public static void BuildPlayerHandler(BuildPlayerOptions obj)
        {
            throw new BuildPlayerWindow.BuildMethodException("Uniton Plus or Uniton Pro is needed to build standalone. You can get them at https://github.com/sponsors/uniton-dev. Otherwise, you can build your project without Uniton by removing the uniton.dll from the assets.");
        }
    }


    class FreeBuildProcessor : IPreprocessBuildWithReport{
        public int callbackOrder { get { return 0; } }
        public void OnPreprocessBuild(BuildReport report){
            // Debug.Log("MyCustomBuildProcessor.OnPreprocessBuild for target " + report.summary.platform + " at path " + report.summary.outputPath);j
//            throw new Exception("Uniton Plus or Uniton Pro is needed to build standalone");
        }
    }


    class Flavor{
        public static string  name = "Free";
        UnityEditor.SceneManagement.EditorSceneManager stest; // will fail during compile of standalone

    }

}