# Uniton

possible domains: uniton.dev, uniton.link, https://www.hover.com/domains/results?q=uniton.io

mailchimp tutorial: https://www.youtube.com/watch?v=9i_WVm5LPSc



Slogan: Instrumentalize Unity!


### Making Uniton More Principled
We could make a strongly typed version of Uniton which would have many advantages. We would know at call time whether an object has a certain member. We would also know what types members have. 

It would probably make most sense to lazily load members for each type. After bootstrapping, whenever a function is called that returns a certain type we can block and load the type's information.

Overloaded functions aren't a problem since they can't have different return types.



### Uploading example binaries to Github releases
Github releases allows files up to 2GB

How to upload via bash: https://gist.github.com/stefanbuck/ce788fee19ab6eb0b4447a85fc99f447#file-upload-github-release-asset-sh-L24