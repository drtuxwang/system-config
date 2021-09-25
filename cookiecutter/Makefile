default: help

.PHONY: docker
docker:       # Create new Docker project
	cookiecutter docker

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
