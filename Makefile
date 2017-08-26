default: check

test: check

check: jsonformat py_compile requirements pep8 pylint unittest
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
	umask 022 && python3 -m pip install -q -r etc/python3-requirements.txt

pep8:
	@echo "\n*** Running Python 3 PEP8 check ***"
	python3 -m pep8 --max-line-length=79 bin/*.py

pylint:
	@echo "\n*** Running Python 3 LINT check ***"
	python3 -m pylint --disable=locally-disabled,locally-enabled --max-line-length=79 \
		--rcfile=/dev/null --output-format=parseable --reports=n -j 2 bin/*.py

unittest:
	@echo "\n*** Running Python 3 UNITTEST check ***"
	python3 -m unittest discover --buffer bin
