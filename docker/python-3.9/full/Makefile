BASE_IMAGE := drtuxwang/python:3.9-slim-bullseye
IMAGE := drtuxwang/python-full:3.9-slim-bullseye
NAME := python39-full
HOSTNAME := python39-full
DOCKER_BUILD_FLAGS ?=
DOCKER_RUN_FLAGS ?=
DOCKER_RUN_COMMAND ?=

DOCKER_RUN_FLAGS := \
	--rm \
	--interactive \
	--tty \
	--cpu-quota=1000000 \
	--cpu-shares=50000 \
	--memory=2000m \
	--memory-reservation=50m \
	--name $(NAME) \
	--hostname $(NAME) \
	$(DOCKER_RUN_FLAGS)


.PHONY: default
default: build status # Default

.PHONY: status
status:              # Status of Docker images
	@make --no-print-directory -C .. status

.PHONY: build
build:               # Build Docker images
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	../../bin/create-rootfs.sh bash bin python3.9 vim
	docker build $(DOCKER_BUILD_FLAGS) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	rm -rf rootfs

.PHONY: run
run:                 # Run Docker container
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: test
test:                # Run tests
	docker run \
		--rm \
		--volume=$(shell realpath ../../..):/vol/app:ro \
		--workdir=/vol/app \
		$(IMAGE) \
		make test

.PHONY: version
version:             # Check versions
	@docker run --rm --entrypoint gcc $(IMAGE) --version 2> /dev/null | grep ^gcc | \
		sed -e "s/([^)]*)//" | awk '{printf("'$(shell pwd)': gcc %s\n", $$2)}'

.PHONY: rmi
rmi:                 # Remove Docker images
	docker rmi -f $(IMAGE) ||:

.PHONY: help
help:                # Show Makefile options
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
