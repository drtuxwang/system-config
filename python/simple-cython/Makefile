# PHONY targets
.PHONY: pull build run version clean

default: test py_compile pycodestyle pylint unittest build run clean

test: py_compile pycodestyle pylint unittest
	@echo "\n*** Tests successfull ***"

py_compile:
	@echo "\n*** Running Python 3 compilation check ***"
	python3 -m py_compile *.pyx
	rm -rf __pycache__

pycodestyle:
	@echo "\n*** Running Python 3 PYCODESTYLE (PEP8) check ***"
	python3 -m pycodestyle --max-line-length=79 *.pyx

pylint:
	@echo "\n*** Running Python 3 PYLINT check ***"
	python3 -m pylint --disable=locally-disabled,locally-enabled --max-line-length=79 \
		--rcfile=/dev/null --output-format=parseable --reports=n -j 2 *.pyx

unittest:
	@echo "\n*** Running Python 3 UNITTEST check ***"
	python3 -m unittest discover --buffer .

build: clean test
	@echo "\n*** Building Cython example ***"
	python3 -m Cython.Build.Cythonize --build -3 cython_example.pyx

run:
	@echo "\n*** Running Cython example ***"
	./run.py

clean:
	rm -rf build *.c *.so

