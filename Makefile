
UNITON_PUBLIC:="${HOME}/dev/uniton"
DLL_NAME:="uniton.dll"
UNITON_VERSION=$(python protocol.py version)
RELEASE_MESSAGE:='new versioning system'

test:
	echo ${UNITON_VERSION}

proto:
	python protocol.py py > py/uniton/protocol.py
	python protocol.py cs > cs/src/Protocol.cs

landing-page:
	# publish landing page to Github
	cp -r public/* ${UNITON_PUBLIC}
	pushd ${UNITON_PUBLIC} && git add . && git commit -m ${RELEASE_MESSAGE} && git push; popd
	#pushd cs; NAME=${DLL_NAME} make; cp out/${DLL_NAME} ${UNITON_PUBLIC}/; popd

landing-page-tag:
	pushd ${UNITON_PUBLIC} && git tag -a v${UNITON_VERSION} -m ${RELEASE_MESSAGE} && git push --follow-tags; popd

landing-page-asset:
	bash upload-github-release-asset.sh github_api_token=${GITHUB_PUBLIC_REPO_TOKEN} owner=rmst repo=uniton tag=v${UNITON_VERSION} filename=./cs/out/uniton.dll

dev-release:
	make proto
	git add .; git commit -m "${RELEASE_MESSAGE}"; git push
	git tag -a v${UNITON_VERSION} -m ${RELEASE_MESSAGE}
	git push --follow-tags

cs-release:
	pushd cs; make dlls; popd
	make landing-page
	make landing-page-tag

py-release:
	# publish to PyPi
	pushd py; make public; popd


