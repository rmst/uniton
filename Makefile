
UNITON_PUBLIC="${HOME}/dev/uniton/"
UNITON_VERSION="0.1.4"
DLL_NAME="uniton.dll"

all:

landing-page:
	cp Readme.md ${UNITON_PUBLIC}
	pushd cs; NAME=${DLL_NAME} make; cp out/${DLL_NAME} ${UNITON_PUBLIC}; popd

publish-landing-page:
	# publish landing page to Github
	make landing-page
	pushd ${UNITON_PUBLIC}; git add .; git commit -m "publish"; git push; popd

publish:
	# publish to PyPi
	echo ${UNITON_VERSION} > py/VERSION
	git add .; git commit -m "v${UNITON_VERSION}"; git push
	git tag -a v${UNITON_VERSION} -m "Published to PyPi"
	git push --follow-tags

	pushd py; make public; popd

	make publish-landing-page


