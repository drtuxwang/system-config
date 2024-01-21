.PHONY: default
default: test         # Default

.PHONY: test
test:                 # Run tests
	@echo "\n*** Running JSON PYCODESTYLE (PEP8) check ***"
	python3 -m pycodestyle --max-line-length=255 *.json
	@echo "\n*** Tests successfull ***"

.PHONY: help
help:                 # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
