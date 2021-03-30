






### How to make it work with more recent Unity versions
In Unity 2020.1.2:
1) New project (3D Built-in [default] Render Pipeline);
2) Window->Package Manager: Add post-processing package;
3) Switch "Project Settings->Player->Other Settings->Rendering->Color Space to 'Linear'" (fixes smeary black stripes on road surfaces);
4) Import Windridge City
5) Switch "Directional Light" in scene from realtime to mixed & static? << Not sure I needed this
6) Switch "Windows->Rendering->Lighting->Lightmapper Settings->Lightmapper" to "Progressive GPU";
7) Uncheck "Realtime Lighting->Realtime Global Illumination (Deprecated)"; (7 & 8 fix lighting "pop" between LOD0 and LOD1)
8) Turn on "Stitch seams" on "popping" building mesh renderer prefabs at all LODs? << Seems to have fixed weird triangles in lighting; increases bake time https://docs.unity3d.com/Manual/Lightmapping-SeamStitching.html
9) Hit "Generate Lighting" - Took about 10 minutes on my GTX 1070;
"There are 535 objects in the Scene with overlapping UV's" << I will completely ignore these:D
A) Set "Edit->Project Settings->Quality->[Ultra] Shadow Distance" to 300 (from 150; stops the shadow being visibly drawn in as you drive along roads in the city, although maybe with mixed directional light this is unnecessary).

I also set Lightmap Resolution to 16 and Padding to 4 for now (were 4 and 2 IIRC), not sure I needed to tbh.
So, it's better, but still not great (see below).

If anyone has a specific idiot's guide or decent tutorial to recommend for this stuff, I'd love to hear about it, I've been 4+ hours so far trying to wrap my head around this (I'm a physics/ gameplay programmer, no background in lighting at all:).
I'd quite like this to "just work".
I then looked at the LOD Group fade mode, and setting the building prefabs to do an animated fade is looking OK (you need to download Unity's standard shader source code, uncomment the lines about fading that the comments tell you to uncomment, then use that instead of Unity's default standard shader for this to work).

I was trying to start completely from scratch and document all of my changes properly, but post-bake it was giving me loads of weird errors for some reason so I've given up.

I think the TL;DR of this is, it would have been great to have had all of the project settings with the original asset, and those in a state where everything is working nicely without pop etc.