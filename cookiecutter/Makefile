default: help

.PHONY: docker
docker:
	cookiecutter docker

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
