default: check

test: check

check: jsonformat py_compile requirements pycodestyle pylint unittest
	@echo "\n*** Tests successfull ***"

jsonformat:
	@echo "\n*** Running JSON formatting ***"
	find -name '*.json' -exec bin/jsonformat {} +

py_compile:
	@echo "\n*** Running Python 3 compilation check ***"
	python3 -m py_compile bin/*.py
	rm -rf */__pycache__

requirements:
	@echo "\n*** Running Python 3 requirements check ***"
	umask 022 && python3 -m pip install -r etc/python3-requirements.txt 2>&1

pycodestyle:
	@echo "\n*** Running Python 3 PYCODESTYLE (PEP8) check ***"
	python3 -m pycodestyle --max-line-length=79 bin/*.py

pylint:
	@echo "\n*** Running Python 3 PYLINT check ***"
	python3 -m pylint --disable=locally-disabled,locally-enabled --max-line-length=79 \
		--rcfile=/dev/null --output-format=parseable --reports=n -j 2 bin/*.py

unittest:
	@echo "\n*** Running Python 3 UNITTEST check ***"
	python3 -m unittest discover --buffer bin
