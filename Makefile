default: test

.PHONY: test
test: check lint

.PHONY: check
check:
	@echo "\n*** Running Python 3 requirements check ***"
	umask 022 && python3 -m pip install -q -r etc/python-requirements.txt
	@echo "\n*** Running Python 3 compilation check ***"
	python3 -m py_compile bin/*.py
	rm -rf */__pycache__
	@echo "\n*** Running Python 3 UNITTEST check ***"
	python3 -m unittest discover --buffer bin
	@echo "\n*** Running BSON/JSON/YAML check ***"
	PATH=`pwd`/bin:${PATH} find -regex '.*[.]\(bson\|json\|ya?ml\)' -exec bin/chkconfig {} +
	@echo "\n*** Check successfull ***"

.PHONY: lint
lint:
	@echo "\n*** Running Python 3 PYFLAKES checks ***"
	python3 -m pyflakes bin/*.py
	@echo "\n*** Running Python 3 PYCODESTYLE (PEP8) checks ***"
	python3 -m pycodestyle --max-line-length=79 bin/*.py
	@echo "\n*** Running Python 3 PYLINT checks ***"
	python3 -m pylint --disable=locally-disabled,locally-enabled --max-line-length=79 \
		--rcfile=/dev/null --output-format=parseable --reports=n -j 2 bin/*.py
	@echo "*** Lint successfull ***"
