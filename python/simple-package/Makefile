default: build

.PHONY: test
test: check lint
	@echo "\n*** Tests successfull ***"

.PHONY: check
check:
	@echo "\n*** Running Python 3 compilation check ***"
	python3 -m py_compile *.py */*.py
	rm -rf __pycache__ */__pycache__
	@echo "\n*** Running Python 3 UNITTEST check ***"
	python3 -m unittest discover --buffer .
	@echo "\n*** Check successfull ***"

.PHONY: lint
lint:
	@echo "\n*** Running Python 3 PYCODESTYLE (PEP8) check ***"
	python3 -m pycodestyle --ignore=E402 --max-line-length=79 *.py */*.py
	@echo "\n*** Running Python 3 PYLINT check ***"
	python3 -m pylint --disable=locally-disabled,locally-enabled --max-line-length=79 \
		--rcfile=/dev/null --output-format=parseable --reports=n -j 2 *.py */*.py
	@echo "*** Lint successfull ***"

.PHONY: lint
build: clean test
	@echo "\n*** Building Python packages ***"
	python3 setup.py bdist_egg
	python3 setup.py bdist_wheel
	ls -l dist/*
	@echo "\n*** Building packages successfull ***"

.PHONY: run
run:
	@echo "\n*** Running simple package example ***"
	PYTHONPATH=`pwd`/dist ./run.py

.PHONY: clean
clean:
	rm -rf build dist simple.egg-info
