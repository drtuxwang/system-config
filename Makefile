PYTHONDONTWRITEBYTECODE := 1
PYTHONS_VERSIONS := 3.12 3.11 3.10 3.9 3.8 3.7 3.6 3.5 2.7
BROWSER := firefox

ifndef PYTHON
	PYTHON := python3
endif


.PHONY: default
default: test         # Default

.PHONY: doc
doc:                  # View README.md as HTML in browser
	bin/markdown README.md
	$(BROWSER) README.xhtml

.PHONY: test
test: check-makefile check-config check-python  # Run tests
	@echo "\n*** Tests all successfull ***"

.PHONY: test-docker
test-docker:          # Run tests in docker
	make --no-print-directory --directory docker test

.PHONY: test-all
test-all: test        # Run tests for all versions
	@for VERSION in $(PYTHONS_VERSIONS); do \
		case $$VERSION in \
		3.[56]) \
			PYTHON=python$$VERSION make --no-print-directory check-python-pip || exit 1; \
			;; \
		3.[7-9]|3.??) \
			PYTHON=python$$VERSION make --no-print-directory check-python-pip || exit 1; \
			PYTHON=python$$VERSION make --no-print-directory check-python-test || exit 1; \
			PYTHON=python$$VERSION make --no-print-directory check-python-lint || exit 1 \
			;; \
		esac; \
	done

.PHONY: check-makefile
check-makefile:       # Check Makefile files
	@echo "\n*** Running Makefile check ***"
	find -name Makefile -exec grep -E -n "^[A-Za-z0-9_-]+:" {} + | grep -E -v ":[^:]*:.{20}...*#" && exit 1 ||:
	find -name Makefile -exec grep -E -n "^[A-Za-z0-9_-]+:  +[a-z]" {} + && exit 1 ||:

.PHONY: check-config
check-config:         # Check all config files
	@echo "\n*** Running BSON/JSON/YAML check ***"
	find -regex '.*[.]\(bson\|json\|ya?ml\)' -exec bin/chkconfig {} + > /dev/null

.PHONY: check-python
check-python:         # Check Python code
	@make --no-print-directory check-python-pip
	@make --no-print-directory check-python-test
	@make --no-print-directory check-python-lint
	@make --no-print-directory check-python-types

.PHONY: check-python-pip
check-python-pip:     # Check python ackages
	@echo "\n*** Running \"${PYTHON}\" package requirement checks ***"
	etc/python-packages.bash -c ${PYTHON}

.PHONY: check-python-test
check-python-test:    # Check python tests
	@echo "\n*** Running \"${PYTHON}\" UNITTEST check ***"
	${PYTHON} -m unittest discover --buffer bin
	@echo "\n*** Running \"${PYTHON}\" COOKIECUTTER check ***"
	@make --no-print-directory --directory cookiecutter test
	@echo "\n*** Running \"${PYTHON}\" PYFLAKES checks ***"
	${PYTHON} -m pyflakes bin/*.py
	@echo "\n*** Running \"${PYTHON}\" PYCODESTYLE (PEP8) checks ***"
	${PYTHON} -m pycodestyle --max-line-length=79 bin/*.py

.PHONY: check-python-lint
check-python-lint:    # Check Python code linting
	@echo "\n*** Running \"${PYTHON}\" PYLINT checks ***"
	${PYTHON} -m pylint --rcfile=.pylintrc bin/*.py

.PHONY: check-python-types
check-python-types:   # Check Python code types
	@echo "*** Running \"${PYTHON}\" MYPY type checks ***"
	mypy --disallow-untyped-defs --no-strict-optional --follow-imports=error --cache-dir=/dev/null bin/*.py

.PHONY: install
install:              # Install Python packages
	@echo "\n*** Installing Python 3 requirements ***"
	etc/python-packages.bash -i ${PYTHON}

.PHONY: diff
diff:                 # Show differences in branch from origin/main
	git fetch ||:
	git diff origin/main

.PHONY: xdiff
xdiff:                # Show graphical differences in branch from origin/main
	git fetch ||:
	git difftool --tool=meld --dir-diff origin/main

.PHONY: reset
reset:                # Ignore differences and reset to origin/<branch>
	git status
	git fetch origin
	git reset --hard origin/`git rev-parse --abbrev-ref HEAD`
	@make --no-print-directory time

.PHONY: time
time:                 # Set file timestamps to git commit times (last 7 days)
	@echo "\n*** Fixing git timestamps (last 7 days) ***"
	find * -type f -mtime -7 | xargs git time

.PHONY: time-all
time-all:             # Set file timestamps to git commit times (all files)
	@echo "\n*** Fixing git timestamps (all files)***"
	find * -type f | xargs git time

.PHONY: gc
gc:                   # Run git garbage collection
	@du -s $(shell pwd)/.git
	rm -rf .git/lfs
	git \
		-c gc.reflogExpire=0 \
		-c gc.reflogExpireUnreachable=0 \
		-c gc.rerereresolved=0 \
		-c gc.rerereunresolved=0 \
		-c gc.pruneExpire=now gc \
		--aggressive
	@du -s $(shell pwd)/.git

.PHONY: help
help:                 # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
