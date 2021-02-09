# FOR SECURITY PLEASE DO NOT enable debug and public access together
# export FLASK_DEBUG=1
# export FLAGS="--host=0.0.0.0"
FLASK_APP = "simple_flask"
FLAGS =


default: test

.PHONY: test
test: check lint
	@echo "\n*** Tests successfull ***"

.PHONY: check
check:
	@echo "\n*** Running Python 3 compilation check ***"
	python3 -m py_compile *.py
	rm -rf __pycache__
	@echo "\n*** Running Python 3 UNITTEST check ***"
	python3 -m unittest discover --buffer .
	@echo "\n*** Check successfull ***"

.PHONY: lint
lint:
	@echo "\n*** Running Python 3 PYCODESTYLE (PEP8) check ***"
	python3 -m pycodestyle --max-line-length=79 *.py
	@echo "\n*** Running Python 3 PYLINT check ***"
	python3 -m pylint --disable=locally-disabled,locally-enabled --max-line-length=79 \
		--rcfile=/dev/null --output-format=parseable --reports=n -j 2 *.py
	@echo "*** Lint successfull ***"

.PHONY: run
run:
	@echo "\n*** Running Flask app ***"
	FLASK_APP=$(FLASK_APP) python3 -m flask run $(FLAGS)

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
