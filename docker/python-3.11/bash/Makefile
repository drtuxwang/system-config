BASE_IMAGE := drtuxwang/python:3.11-slim-bookworm
IMAGE := drtuxwang/python-bash:3.11-slim-bookworm
NAME := python311-bash
HOSTNAME := python311-bash
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
	--name $(NAME) \
	--hostname $(NAME)


.PHONY: default
default: build status # Default

.PHONY: status
status:               # Status of Docker images
	@make --no-print-directory --directory .. status

.PHONY: build
build:                # Build Docker images
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	../../bin/create-rootfs.bash bash bin vim
	$(DOCKER_BUILD) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	rm -rf rootfs

.PHONY: run
run:                  # Run Docker container
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	$(DOCKER_RUN) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: version
version:              # Check versions
	@docker run --rm --entrypoint=python3 $(IMAGE) --version 2> /dev/null | \
		sed -e "s@^@$(shell pwd): @"

.PHONY: rmi
rmi:                  # Remove Docker images
	docker rmi -f $(IMAGE) $(BASE_IMAGE) ||:

.PHONY: help
help:                 # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
