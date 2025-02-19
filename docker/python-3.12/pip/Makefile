BASE_IMAGE := drtuxwang/python:3.12-slim-bookworm
IMAGE := drtuxwang/python-pip:3.12-slim-bookworm
NAME := python312-pip
HOSTNAME := python312-pip
DOCKER_BUILD := docker buildx build $(DOCKER_BUILD_FLAGS)
ifeq ($(shell docker --help | grep -c buildx), 0)
	DOCKER_BUILD := docker build
endif
ifdef http_proxy
	DOCKER_BUILD := $(DOCKER_BUILD) \
		--build-arg http_proxy=$(http_proxy) \
		--build-arg https_proxy=$(https_proxy) \
		--build-arg no_proxy=$(no_proxy)
endif
DOCKER_RUN := docker run \
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
status:               # Status of Docker images
	@make --no-print-directory --directory .. status

.PHONY: build
build:                # Build Docker images
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	../../bin/create-rootfs.bash bash bin python3 vim
	$(DOCKER_BUILD) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	rm -rf rootfs

.PHONY: build-no-cache
build-no-cache:       # Build Docker image with no cache
	@DOCKER_BUILD_FLAGS="--no-cache" make --no-print-directory build

.PHONY: push-stable
push-stable:          # Tag and push stable Docker images
	../../../bin/docker-tag ${IMAGE} `echo ${IMAGE} | sed -e "s/:.*/:stable/"`
	docker push ${IMAGE}
	docker push `echo ${IMAGE} | sed -e "s/:.*/:stable/"`

.PHONY: pull-stable
pull-stable:          # Pull stable Docker image
	docker pull ${IMAGE}
	docker pull `echo ${IMAGE} | sed -e "s/:.*/:stable/"`

.PHONY: run
run:                  # Run Docker container
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	$(DOCKER_RUN) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: test
test:                 # Run tests
	docker run \
		--rm \
		--volume=$(shell realpath ../../..):/vol/app:ro \
		--workdir=/vol/app \
		$(IMAGE) \
		make test

.PHONY: version
version:              # Check versions
	@docker run --rm --entrypoint gcc $(IMAGE) --version 2> /dev/null | grep ^gcc | \
		sed -e "s/([^)]*)//" | awk '{printf("'$(shell pwd)': gcc %s\n", $$2)}'

.PHONY: rmi
rmi:                  # Remove Docker images
	docker rmi -f $(IMAGE) ||:

.PHONY: help
help:                 # Show Makefile options
	@grep "^[A-Za-z0-9].*:" $(lastword $(MAKEFILE_LIST))
