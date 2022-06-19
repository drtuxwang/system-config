PYTHONDONTWRITEBYTECODE := 1
PYTHONS_OLD := 2.7 3.5
PYTHONS_NEW := 3.6 3.7 3.8 3.9 3.10
BROWSER := firefox

ifndef PYTHON
	PYTHON := python3
endif


.PHONY: default
default: test        # Default

.PHONY: test
test: check-makefile check-config check-python-pkg check-python # Run tests
	@echo "\n*** Tests all successfull ***"

.PHONY: test-docker
test-docker:         # Run tests in docker
	make --no-print-directory -C docker test

.PHONY: test-python
test-python:         # Test Python (all versions)
	@for VERSION in $(PYTHONS_OLD); do \
		PYTHON=python$$VERSION make --no-print-directory check-python-packages || exit 1; \
	done
	@for VERSION in $(PYTHONS_NEW); do \
		PYTHON=python$$VERSION make --no-print-directory check-python-packages || exit 1; \
		PYTHON=python$$VERSION make --no-print-directory check-python || exit 1; \
	done

.PHONY: check-makefile-help
check-makefile:      # Check Makefile files
	@echo "\n*** Running Makefile check ***"
	find -name Makefile -exec egrep -n "^[A-Za-z0-9_-]+:" {} + | egrep -v ":[^:]*:.{20}..*#" && exit 1 ||:

.PHONY: check-config
check-config:        # Check all config files
	@echo "\n*** Running BSON/JSON/YAML check ***"
	find -regex '.*[.]\(bson\|json\|ya?ml\)' -exec bin/chkconfig {} +

.PHONY: check-python-packages
check-python-pkg:    # Check Python packages
	@echo "\n*** Running \"${PYTHON}\" package requirement checks ***"
	etc/python-packages.sh ${PYTHON}

.PHONY: check-python
check-python:        # Check Python code
	@echo "\n*** Running \"${PYTHON}\" UNITTEST check ***"
	${PYTHON} -m unittest discover --buffer bin
	@echo "\n*** Running \"${PYTHON}\" COOKIECUTTER check ***"
	make --no-print-directory -C cookiecutter test
	@echo "\n*** Running \"${PYTHON}\" PYFLAKES checks ***"
	${PYTHON} -m flake8 bin/*.py
	@echo "\n*** Running \"${PYTHON}\" PYCODESTYLE (PEP8) checks ***"
	${PYTHON} -m pycodestyle --max-line-length=79 bin/*.py
	@echo "\n*** Running \"${PYTHON}\" PYLINT checks ***"
	${PYTHON} -m pylint --rcfile=.pylintrc bin/*.py
	@echo "*** Running \"${PYTHON}\" MYPY type checks ***"
	${PYTHON} -m mypy --disallow-untyped-defs --no-strict-optional --cache-dir=/dev/null bin/*.py

.PHONY: install
install:             # Install Python packages
	@echo "\n*** Installing Python 3 requirements ***"
	etc/python-packages.sh -i ${PYTHON}

.PHONY: gc
gc:                  # Run git garbage collection
	@du -s $(shell pwd)/.git
	git \
		-c gc.reflogExpire=0 \
		-c gc.reflogExpireUnreachable=0 \
		-c gc.rerereresolved=0 \
		-c gc.rerereunresolved=0 \
		-c gc.pruneExpire=now gc \
		--aggressive
	@du -s $(shell pwd)/.git

.PHONY: doc
doc:                 # View README.md as HTML in browser
	$(PYTHON) -m markdown README.md > README.html
	$(BROWSER) README.html

.PHONY: help
help:                # Show Makefile options
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
