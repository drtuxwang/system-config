ifndef PYTHON
	PYTHON := python3
endif


.PHONY: default
default: help         # Default

.PHONY: docker
docker:               # Create new Docker project
	${PYTHON} -m cookiecutter docker

.PHONY: test
test:                 # Test new Docker project
	rm -rf my_project
	${PYTHON} -m cookiecutter --no-input docker
	rm -rf my_project

.PHONY: help
help:                 # Show Makefile options
	@grep "^[A-Za-z0-9].*:" $(lastword $(MAKEFILE_LIST))
