ifndef PYTHON
	PYTHON := python3
endif


.PHONY: default
default: help        # Default

.PHONY: docker
docker:              # Create new Docker project
	${PYTHON} -m cookiecutter docker

.PHONY: test
test:                # Test new Docker project
	${PYTHON} -m cookiecutter --no-input docker
	rm -rf my_project

.PHONY: help
help:                # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
