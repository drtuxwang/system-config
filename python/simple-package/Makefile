.PHONY: default
default: build       # Default

.PHONY: test
test:                # Run test
	@echo "\n*** Running Python 3 compilation check ***"
	python3 -m py_compile *.py */*.py
	rm -rf __pycache__ */__pycache__
	@echo "\n*** Running Python 3 UNITTEST check ***"
	python3 -m unittest discover --buffer .
	@echo "\n*** Running Python 3 PYCODESTYLE (PEP8) check ***"
	python3 -m pycodestyle --ignore=E402 --max-line-length=79 *.py */*.py
	@echo "\n*** Running Python 3 PYLINT check ***"
	python3 -m pylint --disable=locally-disabled,locally-enabled --max-line-length=79 \
		--rcfile=/dev/null --output-format=parseable --reports=n -j 2 *.py */*.py
	@echo "*** Lint successfull ***"
	@echo "\n*** Tests successfull ***"

.PHONY: build
build: clean test    # Build package
	@echo "\n*** Building Python packages ***"
	python3 setup.py bdist_egg
	python3 setup.py bdist_wheel
	ls -l dist/*
	@echo "\n*** Building packages successfull ***"

.PHONY: run
run:                 # Run Python code
	@echo "\n*** Running simple package example ***"
	PYTHONPATH=`pwd`/dist ./run.py

.PHONY: clean
clean:               # Remove temporary build files
	rm -rf build dist simple.egg-info

.PHONY: help
help:                # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
