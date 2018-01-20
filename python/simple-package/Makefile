default: build

clean:
	rm -rf build dist simple.egg-info

test: py_compile pycodestyle pylint unittest
	@echo "\n*** Tests successfull ***"

py_compile:
	@echo "\n*** Running Python 3 compilation check ***"
	python3 -m py_compile *.py */*.py
	rm -rf __pycache__ */__pycache__

pycodestyle:
	@echo "\n*** Running Python 3 PYCODESTYLE (PEP8) check ***"
	python3 -m pycodestyle --ignore=E402 --max-line-length=79 *.py */*.py

pylint:
	@echo "\n*** Running Python 3 LINT check ***"
	python3 -m pylint --disable=locally-disabled,locally-enabled --max-line-length=79 \
		--rcfile=/dev/null --output-format=parseable --reports=n -j 2 *.py */*.py

unittest:
	@echo "\n*** Running Python 3 UNITTEST check ***"
	python3 -m unittest discover --buffer .

build: clean test
	@echo "\n*** Building Python packages ***"
	python3 setup.py bdist_egg
	python3 setup.py bdist_wheel
	ls -l dist/*
	@echo "\n*** Building packages successfull ***"

run:
	@echo "\n*** Running simple package example ***"
	PYTHONPATH=`pwd`/dist ./run.py
