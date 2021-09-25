default: test

.PHONY: test
test:         # Run test
	@echo "\n*** Running Python 3 compilation check ***"
	python3 -m py_compile *.py
	rm -rf __pycache__
	@echo "\n*** Running Python 3 UNITTEST check ***"
	python3 -m unittest discover --buffer .
	@echo "\n*** Running Python 3 PYCODESTYLE (PEP8) check ***"
	python3 -m pycodestyle --max-line-length=79 *.py
	@echo "\n*** Running Python 3 PYLINT check ***"
	python3 -m pylint --disable=locally-disabled,locally-enabled --max-line-length=79 \
		--rcfile=/dev/null --output-format=parseable --reports=n -j 2 *.py
	@echo "\n*** Tests successfull ***"

.PHONY: run
run:          # Run Python code
	@echo "\n*** Running Tornado web server ***"
	./tornado_server.py

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
