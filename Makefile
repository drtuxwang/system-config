PYTHONDONTWRITEBYTECODE := 1
PYTHONS_VERSIONS := 3.13 3.12 3.11 3.10 3.9 3.8 3.7 2.7
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
		3.7) \
			PYTHON=python$$VERSION make --no-print-directory check-python-pip || exit 1; \
			PYTHON=python$$VERSION make --no-print-directory check-python-test || exit 1; \
			;; \
		3.[8-9]|3.??) \
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
	@echo "\n*** Running BSON/JSON/XML/YAML check ***"
	find -regex '.*[.]\(bson\|xhtml\|json\|xml\|ya?ml\)' -exec bin/chkconfig {} +

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

.PHONY: time
time:                 # Set file timestamps to git commit times (last 7 days)
	@echo "\n*** Fixing git timestamps (last 7 days) ***"
	find * -type f -mtime -7 | xargs -r git time

.PHONY: time-all
time-all:             # Set file timestamps to git commit times (all files)
	@echo "\n*** Fixing git timestamps (all files)***"
	find * -type f | xargs -r git time

.PHONY: diff
diff:                 # Show commit changes in branch
	git fetch ||:
	git diff origin/`git rev-parse --abbrev-ref origin/HEAD | sed -e "s@.*/@@"`..HEAD

.PHONY: xdiff
xdiff:                # Show graphical commit changes in branch
	git fetch ||:
	git difftool --tool=meld --dir-diff origin/`git rev-parse --abbrev-ref origin/HEAD | sed -e "s@.*/@@"`..HEAD

.PHONY: squash
squash:               # Squash all commits in branch
	git fetch origin
	git reset --soft `git merge-base HEAD origin/main`
	git status

.PHONY: reset
reset:                # Ignore differences and reset to origin/<branch>
	git status
	git fetch origin
	git reset --hard origin/`git rev-parse --abbrev-ref HEAD`
	@make --no-print-directory time

.PHONY: ref
ref:                  # Show git branch/tags hash references
	git show-ref
	git lfs ls-files --size --all

.PHONY: gc
gc:                   # Run git garbage collection
	@du -s $(shell pwd)/.git
	rm -rf .git/lfs
	git fsck
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
	@grep "^[A-Za-z0-9].*:" $(lastword $(MAKEFILE_LIST))
