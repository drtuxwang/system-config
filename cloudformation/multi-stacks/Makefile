default: test

.PHONY: test
test: lint
	@echo "\n*** Tests successfull ***"

.PHONY: lint
lint:
	@echo "\n*** Running JSON PYCODESTYLE (PEP8) check ***"
	python3 -m pycodestyle --max-line-length=255 *.json

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
