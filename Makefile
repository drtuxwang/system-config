PYTHONDONTWRITEBYTECODE := 1
PYTHONS_OLD := 2.7 3.5
PYTHONS_NEW := 3.6 3.7 3.8 3.9 3.10
BROWSER := firefox

ifndef PYTHON
	PYTHON := python3
endif


default: test

.PHONY: doc
doc:
	$(PYTHON) -m markdown README.md > README.html
	$(BROWSER) README.html

.PHONY: test
test: check-config check-python-tests check-python-packages
	@echo "\n*** Tests all successfull ***"

.PHONY: test-all
test-all: check-config
	@for VERSION in $(PYTHONS_OLD); do \
		PYTHON=python$$VERSION make --no-print-directory check-python-packages || exit 1; \
	done
	@for VERSION in $(PYTHONS_NEW); do \
		PYTHON=python$$VERSION make --no-print-directory check-python-tests || exit 1; \
		PYTHON=python$$VERSION make --no-print-directory check-python-packages || exit 1; \
	done
	@echo "\n*** Tests all successfull ***"

.PHONY: check-config
check-config:
	@echo "\n*** Running BSON/JSON/YAML check ***"
	find -regex '.*[.]\(bson\|json\|ya?ml\)' -exec bin/chkconfig {} +

.PHONY: check-python-tests
check-python-tests:
	@echo "\n*** Running \"${PYTHON}\" UNITTEST check ***"
	${PYTHON} -m unittest discover --buffer bin
	@echo "\n*** Running \"${PYTHON}\" PYFLAKES checks ***"
	${PYTHON} -m flake8 bin/*.py
	@echo "\n*** Running \"${PYTHON}\" PYCODESTYLE (PEP8) checks ***"
	${PYTHON} -m pycodestyle --max-line-length=79 bin/*.py
	@echo "\n*** Running \"${PYTHON}\" PYLINT checks ***"
	${PYTHON} -m pylint --rcfile=.pylintrc bin/*.py
	@echo "*** Running \"${PYTHON}\" MYPY type checks ***"
	${PYTHON} -m mypy --disallow-untyped-defs --no-strict-optional --cache-dir=/dev/null bin/*.py

.PHONY: check-python-packages
check-python-packages:
	@echo "\n*** Running \"${PYTHON}\" package requirement checks ***"
	etc/python-packages.sh ${PYTHON}

.PHONY: docker-test
docker-test:  # Run tests in docker
	make -C docker test

.PHONY: install
install:      # Install Python packages
	@echo "\n*** Installing Python 3 requirements ***"
	etc/python-packages.sh -i ${PYTHON}

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
