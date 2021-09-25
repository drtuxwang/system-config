PYTHONDONTWRITEBYTECODE := 1

ifndef PYTHON
	PYTHON := python3
endif


default: test

.PHONY: test
test:         # Run tests
	@echo "\n*** Running \"${PYTHON}\" UNITTEST check ***"
	${PYTHON} -m unittest discover --buffer bin
	@echo "\n*** Running BSON/JSON/YAML check ***"
	find -regex '.*[.]\(bson\|json\|ya?ml\)' -exec bin/chkconfig {} +
	@echo "\n*** Running \"${PYTHON}\" PYFLAKES checks ***"
	${PYTHON} -m flake8 bin/*.py
	@echo "\n*** Running \"${PYTHON}\" PYCODESTYLE (PEP8) checks ***"
	${PYTHON} -m pycodestyle --max-line-length=79 bin/*.py
	@echo "\n*** Running \"${PYTHON}\" PYLINT checks ***"
	${PYTHON} -m pylint --rcfile=.pylintrc bin/*.py
	@echo "*** Running \"${PYTHON}\" MYPY type checks ***"
	mypy --disallow-untyped-defs --no-strict-optional --cache-dir=/dev/null bin/*.py
	@echo "\n*** Check successfull ***"

.PHONY: docker-test
docker-test:  # Run tests in docker
	make -C docker test

.PHONY: install
install:      # Install Python packages
	@echo "\n*** Installing Python 3 requirements ***"
	etc/install-python-requirements.sh `which ${PYTHON}`

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
