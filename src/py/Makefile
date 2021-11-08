# The following variables should be set
#	export TWINE_USERNAME='...'
#	export TWINE_PASSPORT='...'

all:

public:
	pip install twine
	python setup.py sdist bdist_wheel
	twine upload dist/*
	rm -rf dist build