default: test py_compile pycodestyle pylint unittest build run clean

.PHONY: test
test: check lint
	@echo "\n*** Tests successfull ***"

.PHONY: check
check:
	@echo "\n*** Running Python 3 compilation check ***"
	python3 -m py_compile *.pyx
	rm -rf __pycache__
	@echo "\n*** Running Python 3 UNITTEST check ***"
	python3 -m unittest discover --buffer .
	@echo "\n*** Check successfull ***"

.PHONY: lint
lint:
	@echo "\n*** Running Python 3 PYCODESTYLE (PEP8) check ***"
	python3 -m pycodestyle --max-line-length=79 *.pyx
	@echo "\n*** Running Python 3 PYLINT check ***"
	python3 -m pylint --disable=locally-disabled,locally-enabled --max-line-length=79 \
		--rcfile=/dev/null --output-format=parseable --reports=n -j 2 *.pyx
	@echo "*** Lint successfull ***"

.PHONY: build
build: clean test
	@echo "\n*** Building Cython example ***"
	python3 -m Cython.Build.Cythonize --build -3 cython_example.pyx

.PHONY: run
run:
	@echo "\n*** Running Cython example ***"
	./run.py

.PHONY: clean
clean:
	rm -rf build *.c *.so

