
UNITON_PUBLIC:="${HOME}/dev/uniton"
DLL_NAME:="uniton.dll"
UNITON_VERSION:=`python protocol.py version`
RELEASE_MESSAGE:='new versioning system'

test:
	echo ${UNITON_VERSION}

all:

landing-page:
	cp -r public/* ${UNITON_PUBLIC}
	#pushd cs; NAME=${DLL_NAME} make; cp out/${DLL_NAME} ${UNITON_PUBLIC}/; popd

cs-release:
	# publish landing page to Github
	make landing-page
	pushd ${UNITON_PUBLIC}; git add .; git commit -m "${RELEASE_MESSAGE}"; git push; popd
	upload-github-release-asset.sh github_api_token=${GITHUB_PUBLIC_REPO_TOKEN} owner=rmst repo=uniton tag=v${UNITON_VERSION} filename=./cs/out/uniton.dll

proto:
	python protocol.py py > py/uniton/protocol.py
	python protocol.py cs > cs/src/Protocol.cs

new-release:
	make proto

	# publish to PyPi
	git add .; git commit -m "v${UNITON_VERSION}"; git push
	git tag -a v${UNITON_VERSION} -m ${RELEASE_MESSAGE}
	git push --follow-tags

	pushd py; make public; popd

	make landing-page


