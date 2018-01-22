# FOR SECURITY PLEASE DO NOT enable debug and public access together
# export FLASK_DEBUG=1
# export FLAGS="--host=0.0.0.0"
FLASK_APP = "simple_flask"
FLAGS =

default: test

test: py_compile pycodestyle pylint unittest
	@echo "\n*** Tests successfull ***"

py_compile:
	@echo "\n*** Running Python 3 compilation check ***"
	python3 -m py_compile *.py
	rm -rf __pycache__

pycodestyle:
	@echo "\n*** Running Python 3 PYCODESTYLE (PEP8) check ***"
	python3 -m pycodestyle --max-line-length=79 *.py

pylint:
	@echo "\n*** Running Python 3 PYLINT check ***"
	python3 -m pylint --disable=locally-disabled,locally-enabled --max-line-length=79 \
		--rcfile=/dev/null --output-format=parseable --reports=n -j 2 *.py

unittest:
	@echo "\n*** Running Python 3 UNITTEST check ***"
	python3 -m unittest discover --buffer .

run:
	@echo "\n*** Running Flask app ***"
	FLASK_APP=$(FLASK_APP) python3 -m flask run $(FLAGS)
