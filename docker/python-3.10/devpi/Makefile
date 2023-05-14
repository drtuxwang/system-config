BASE_IMAGE := drtuxwang/python:3.10-slim-bullseye
IMAGE := drtuxwang/python-devpi:3.10-slim-bullseye
NAME := python310-devpi
HOSTNAME := python310-devpi
LOCALPORT ?= 8080
DOCKER_BUILD := docker buildx build
ifeq ($(shell docker --help | grep -c buildx), 0)
	DOCKER_BUILD= := docker build
endif
DOCKER_RUN := docker run \
	--rm \
	--interactive \
	--tty \
	--cpu-quota=1000000 \
	--cpu-shares=50000 \
	--memory=1000m \
	--memory-reservation=50m \
	--workdir /var/lib/devpi \
	--publish $(LOCALPORT):8080 \
	--name $(NAME) \
	--hostname $(HOSTNAME)


.PHONY: default
default: build status # Default

.PHONY: status
status:              # Status of Docker images
	@make --no-print-directory --directory .. status

.PHONY: build
build:               # Build Docker images
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	$(DOCKER_BUILD) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .

.PHONY: run
run:                 # Run Docker container
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	$(DOCKER_RUN) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: version
version:             # Check versions
	@docker run --rm --entrypoint devpi-server $(IMAGE) --version 2> /dev/null | \
		   awk '{printf("'$(shell pwd)': devpi-server %s\n", $$1)}'

.PHONY: rmi
rmi:                 # Remove Docker images
	docker rmi -f $(IMAGE) ||:

.PHONY: help
help:                # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
