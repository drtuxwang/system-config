BASE_IMAGE := python:3.12-slim-bookworm
IMAGE := drtuxwang/python:3.12-slim-bookworm
NAME := python312
HOSTNAME := python312
DOCKER_BUILD := docker buildx build $(DOCKER_BUILD_FLAGS)
	$(DOCKER_RUN_FLAGS)
ifeq ($(shell docker --help | grep -c buildx), 0)
	DOCKER_BUILD := docker build
endif
ifdef http_proxy
	DOCKER_BUILD := $(DOCKER_BUILD) \
		--build-arg http_proxy=$(http_proxy) \
		--build-arg https_proxy=$(https_proxy) \
		--build-arg no_proxy=$(no_proxy)
endif
BUILD_DIRS := devpi pip
DOCKER_RUN := docker run \
	--rm \
	--interactive \
	--tty \
	--cpu-quota=1000000 \
	--cpu-shares=50000 \
	--memory=2000m \
	--memory-reservation=50m \
	--name $(NAME) \
	--hostname $(NAME)


.PHONY: default
default: build status # Default

.PHONY: status
status:               # Status of Docker images
	@../../bin/docker-images "^$(BASE_IMAGE) " "`echo $(IMAGE) | sed -e 's/-[^-:]*:/.*:/'` " ||:

.PHONY: pull
pull:                 # Pull Docker base image
	docker pull $(BASE_IMAGE)
	@make --no-print-directory status

.PHONY: pull-save
pull-save:            # Pull updated Docker base image and save to tar archive
	../bin/pull-save.bash $(BASE_IMAGE)

.PHONY: save
save: pull            # Pull Docker base image and save to tar archive
	../../bin/docker-save $(BASE_IMAGE)

.PHONY: build
build:                # Build Docker images
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	../bin/create-rootfs.bash bash bin python3 vim
	$(DOCKER_BUILD) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	rm -rf rootfs
	for DIR in $(BUILD_DIRS); do \
		make --no-print-directory --directory $$DIR build || exit 1; \
	done

.PHONY: build-no-cache
build-no-cache:       # Build Docker image with no cache
	@DOCKER_BUILD_FLAGS="--no-cache" make --no-print-directory build

.PHONY: test
test:                 # Run tests
	make --no-print-directory --directory pip test

.PHONY: run
run:                  # Run Docker container
	make --no-print-directory --directory bash run

.PHONY: version
version:              # Check version
	@docker run --rm --entrypoint gcc $(IMAGE) --version 2> /dev/null | grep ^gcc | \
		sed -e "s/([^)]*)//" | awk '{printf("'$(shell pwd)': gcc %s\n", $$2)}'

.PHONY: rmi
rmi:                  # Remove Docker images
	for DIR in $(BUILD_DIRS); do \
		make --no-print-directory --directory $$DIR rmi; \
	done
	docker rmi -f $(IMAGE) ||:

.PHONY: rmi-base
rmi-base: rmi         # Remove Docker images including base image
	docker rmi -f $(BASE_IMAGE) ||:

.PHONY: help
help:                 # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
