BASE_IMAGE := drtuxwang/alpine:3.14
IMAGE := drtuxwang/alpine-dev:3.14
NAME := alpine314-dev
HOSTNAME := alpine314-dev
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
	--hostname $(HOSTNAME) \
	$(DOCKER_RUN_FLAGS)


.PHONY: default
default: build status

.PHONY: status
status:       # Status of Docker images
	@make --no-print-directory -C .. status

.PHONY: build
build:        # Build Docker images
	../../bin/create-root-tar.sh bash bin vim
	../../bin/python-packages.sh
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	rm -rf tmpdir

.PHONY: run
run:          # Run Docker container
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: version
version:      # Check versions
	@docker run $(DOCKER_RUN_FLAGS) --entrypoint gcc $(IMAGE) --version 2> /dev/null | grep ^gcc | \
		sed -e "s/([^)]*)//" | awk '{printf("'$(shell pwd)': gcc %s\n", $$2)}'

.PHONY: rmi
rmi:          # Remove Docker images
	docker rmi -f $(IMAGE) ||:

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
