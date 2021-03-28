BASE_IMAGE := drtuxwang/python:3.7-slim-buster
IMAGE := drtuxwang/python-bash:3.7-slim-buster
NAME := python37-bash
HOSTNAME := python37-bash
DOCKER_BUILD_FLAGS ?=
DOCKER_RUN_FLAGS ?=
DOCKER_RUN_COMMAND ?=

DOCKER_RUN_FLAGS := \
	--rm \
	--interactive \
	--tty \
	--cpu-quota=1000000 \
	--cpu-shares=50000 \
	--memory=1000m \
	--memory-reservation=50m \
	--name $(NAME) \
	--hostname $(NAME) \
	$(DOCKER_RUN_FLAGS)


.PHONY: default
default: build status

.PHONY: status
status:
	@make --no-print-directory -C .. status

.PHONY: build
build:
	../../bin/create-root-tar bash bin vim
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	rm -rf tmpdir

.PHONY: run
run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: version
version:
	@docker run $(DOCKER_RUN_FLAGS) --entrypoint=python3 $(IMAGE) --version 2> /dev/null | \
		sed -e "s@^@$(shell pwd): @"

.PHONY: rmi
rmi:
	docker rmi -f $(IMAGE) $(BASE_IMAGE) ||:

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
