default: test

test: py_compile requirements pep8 pylint unittest clean
	@echo "\n*** Tests successfull ***"

py_compile:
	@echo "\n*** Running Python 3 compilation check ***"
	python3 -m py_compile bin/*.py
	rm -rf */__pycache__

requirements:
	@echo "\n*** Running Python 3 requirements check ***"
	python3 -m pip install -r requirements.txt

pep8:
	@echo "\n*** Running Python 3 PEP8 check ***"
	python3 -m pep8 --max-line-length=100 bin/*.py

pylint:
	@echo "\n*** Running Python 3 LINT check ***"
	python3 -m pylint --max-line-length=100 -j 2 --reports=n bin/*.py

unittest:
	@echo "\n*** Running Python 3 UNITTEST check ***"
	python3 ./bin/test_pyld.py
