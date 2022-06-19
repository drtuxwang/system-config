.PHONY: default
default: help        # Default

.PHONY: docker
docker:              # Create new Docker project
	cookiecutter docker

.PHONY: test
test:                # Test new Docker project
	cookiecutter --no-input docker
	rm -rf my_project

.PHONY: help
help:                # Show Makefile options
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
