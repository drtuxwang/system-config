PYTHONDONTWRITEBYTECODE := 1


default: test

.PHONY: install
install:
	@echo "\n*** Installing Python 3 requirements ***"
	etc/install-python-requirements.sh `which python3`

.PHONY: test
test: check lint

.PHONY: docker-test
docker-test:
	make -C docker test

.PHONY: check
check:
	@echo "\n*** Running Python 3 requirements check ***"
	umask 022 && python3 -m pip install -q -r etc/python-requirements.txt
	@echo "\n*** Running Python 3 UNITTEST check ***"
	python3 -m unittest discover --buffer bin
	@echo "\n*** Running BSON/JSON/YAML check ***"
	find -regex '.*[.]\(bson\|json\|ya?ml\)' -exec bin/chkconfig {} +
	@echo "\n*** Check successfull ***"

.PHONY: lint
lint:
	@echo "\n*** Running Python 3 PYFLAKES checks ***"
	python3 -m flake8 bin/*.py
	@echo "\n*** Running Python 3 PYCODESTYLE (PEP8) checks ***"
	python3 -m pycodestyle --max-line-length=79 bin/*.py
	@echo "\n*** Running Python 3 PYLINT checks ***"
	python3 -m pylint --rcfile=.pylintrc bin/*.py
	@echo "*** Running Python 3 MYPY type checks ***"
	mypy --disallow-untyped-defs --no-strict-optional --cache-dir=/dev/null bin/*.py
	@echo "\n*** Lint successfull ***"

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
