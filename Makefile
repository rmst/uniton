
UNITON_PUBLIC="${HOME}/dev/uniton/"
UNITON_VERSION="0.1.2"
DLL_NAME="uniton.dll"

all:

landing-page:
	cp Readme.md ${UNITON_PUBLIC}
	pushd cs; NAME=${DLL_NAME} make; cp out/${DLL_NAME} ${UNITON_PUBLIC}; popd

publish-landing-page:
	# publish landing page to Github
	git diff --quiet || (echo 'uncommitted changes - aborting'; exit 1)
	make landing-page
	pushd ${UNITON_PUBLIC}; git add .; git commit -m "publish"; git push; popd

publish:
	# publish to PyPi
	git diff --quiet || (echo 'uncommitted changes - aborting'; exit 1)
	git tag -a v${UNITON_VERSION} -m "Published to PyPi"
	git push --follow-tags

	echo ${UNITON_VERSION} > py/VERSION
	pushd py; make public; popd

	make publish-landing-page


