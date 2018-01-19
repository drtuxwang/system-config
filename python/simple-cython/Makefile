default: build

clean:
	rm -rf build *.c *.so

test: py_compile pycodestyle pylint
	@echo "\n*** Tests successfull ***"

py_compile:
	@echo "\n*** Running Python 3 compilation check ***"
	python3 -m py_compile *.pyx
	rm -rf __pycache__

pycodestyle:
	@echo "\n*** Running Python 3 PYCODESTYLE check ***"
	python3 -m pycodestyle --max-line-length=79 *.pyx

pylint:
	@echo "\n*** Running Python 3 LINT check ***"
	python3 -m pylint --disable=locally-disabled,locally-enabled --max-line-length=79 \
		--rcfile=/dev/null --output-format=parseable --reports=n -j 2 *.pyx

build: clean test
	python3 -m Cython.Build.Cythonize --build -3 cython_example.pyx

run:
	python3 -c 'import cython_example'
