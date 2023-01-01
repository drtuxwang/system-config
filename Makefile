PYTHONDONTWRITEBYTECODE := 1
PYTHONS_VERSIONS := 3.11 3.10 3.9 3.8 3.7 3.6 3.5 2.7
BROWSER := firefox

ifndef PYTHON
	PYTHON := python3
endif


.PHONY: default
default: test        # Default

.PHONY: test
test: check-makefile check-config check-python check-packages # Run tests
	@echo "\n*** Tests all successfull ***"

.PHONY: test-docker
test-docker:         # Run tests in docker
	make --no-print-directory --directory docker test

.PHONY: test-all
test-all: test       # Run tests for all versions
	@for VERSION in $(PYTHONS_VERSIONS); do \
		case $$VERSION in \
		3.[6-9]|3.??) \
			PYTHON=python$$VERSION make --no-print-directory check-python || exit 1 \
			;; \
		esac; \
		PYTHON=python$$VERSION make --no-print-directory check-packages || exit 1; \
	done

.PHONY: check-makefile-help
check-makefile:      # Check Makefile files
	@echo "\n*** Running Makefile check ***"
	find -name Makefile -exec grep -E -n "^[A-Za-z0-9_-]+:" {} + | grep -E -v ":[^:]*:.{20}..*#" && exit 1 ||:
	find -name Makefile -exec grep -E -n "^[A-Za-z0-9_-]+:  +[a-z]" {} + && exit 1 ||:

.PHONY: check-config
check-config:        # Check all config files
	@echo "\n*** Running BSON/JSON/YAML check ***"
	find -regex '.*[.]\(bson\|json\|ya?ml\)' -exec bin/chkconfig {} +

.PHONY: check-python-lint
check-python-lint:   # Check Python code linting
	@echo "\n*** Running \"${PYTHON}\" PYLINT checks ***"
	${PYTHON} -m pylint --rcfile=.pylintrc bin/*.py

.PHONY: check-python-types
check-python-types:  # Check Python code types
	@echo "*** Running \"${PYTHON}\" MYPY type checks ***"
	${PYTHON} -m mypy --disallow-untyped-defs --no-strict-optional --follow-imports=error --cache-dir=/dev/null bin/*.py

.PHONY: check-python
check-python:        # Check Python code
	@echo "\n*** Running \"${PYTHON}\" UNITTEST check ***"
	${PYTHON} -m unittest discover --buffer bin
	@echo "\n*** Running \"${PYTHON}\" COOKIECUTTER check ***"
	@make --no-print-directory --directory cookiecutter test
	@echo "\n*** Running \"${PYTHON}\" PYFLAKES checks ***"
	${PYTHON} -m flake8 bin/*.py
	@echo "\n*** Running \"${PYTHON}\" PYCODESTYLE (PEP8) checks ***"
	${PYTHON} -m pycodestyle --max-line-length=79 bin/*.py
	@make --no-print-directory check-python-lint
	@case ${PYTHON} in \
	python3|python3.9|python3.1?) \
		make --no-print-directory check-python-types \
		;; \
	esac

.PHONY: check-packages
check-packages:      # Check packages
	@echo "\n*** Running \"${PYTHON}\" package requirement checks ***"
	etc/python-packages.sh -c ${PYTHON}

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
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
