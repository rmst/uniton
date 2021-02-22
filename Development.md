# Development

To build and upload the Python package to PyPi run
```bash
export TWINE_USERNAME='SimonRamstedt'
export TWINE_PASSPORT='...'
pip install twine
python setup.py sdist bdist_wheel
twine upload dist/*
```