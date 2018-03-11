default: test

test: check lint

check: py_check config_check
	@echo "\n*** Check successfull ***"

lint: py_lint
	@echo "\n*** Lint successfull ***"

py_check:
	@echo "\n*** Running Python 3 requirements check ***"
	umask 022 && python3 -m pip install -r etc/python3-requirements.txt 2>&1
	@echo "\n*** Running Python 3 compilation check ***"
	python3 -m py_compile bin/*.py
	rm -rf */__pycache__
	@echo "\n*** Running Python 3 UNITTEST check ***"
	python3 -m unittest discover --buffer bin

config_check:
	@echo "\n*** Running JSON check ***"
	PATH=`pwd`/bin:${PATH} find -name '*.json' -exec bin/json -c {} +
	@echo "\n*** Running YAML check ***"
	PATH=`pwd`/bin:${PATH} find -name '*.yml' -exec bin/yaml -c {} +

py_lint:
	@echo "\n*** Running Python 3 PYCODESTYLE (PEP8) check ***"
	python3 -m pycodestyle --max-line-length=79 bin/*.py
	@echo "\n*** Running Python 3 PYLINT check ***"
	python3 -m pylint --disable=locally-disabled,locally-enabled --max-line-length=79 \
		--rcfile=/dev/null --output-format=parseable --reports=n -j 2 bin/*.py

