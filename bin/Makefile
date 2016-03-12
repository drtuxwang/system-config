default: test

test: py_compile pep8 pylint unittest clean
	@echo "\n*** Tests successfull ***"

py_compile:
	@echo "\n*** Running Python 3 compilation check ***"
	python3 -m py_compile *.py

pep8:
	@echo "\n*** Running Python 3 PEP8 check ***"
	python3 -m pep8 --max-line-length=100 *.py

pylint:
	@echo "\n*** Running Python 3 LINT check ***"
	python3 -m pylint --max-line-length=100 -j 2 --reports=n *.py

unittest:
	@echo "\n*** Running Python 3 UNITTEST check ***"
	python3 ./test_pyld.py

clean:
	@echo "\n*** Cleaning ***"
	rm -rf __pycache__

