default: test

test: py_compile pep8 pylint unittest
	@echo "\n*** Tests successfull ***"

py_compile:
	@echo "\n*** Running Python 3 compilation check ***"
	python3 -m py_compile *.py
	rm -rf __pycache__

pep8:
	@echo "\n*** Running Python 3 PEP8 check ***"
	python3 -m pep8 --max-line-length=79 *.py

pylint:
	@echo "\n*** Running Python 3 LINT check ***"
	python3 -m pylint --disable=locally-disabled,locally-enabled --max-line-length=79 \
		--rcfile=/dev/null --output-format=parseable --reports=n -j 2 *.py

unittest:
	@echo "\n*** Running Python 3 UNITTEST check ***"
	python3 -m unittest discover --buffer .