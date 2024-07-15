BASE_IMAGE := registry:2.6
IMAGE := drtuxwang/registry-docker:2.6
NAME := registry26-docker
HOSTNAME := registry26-docker
LOCALPORT ?= 5000
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
	--volume=/var/lib/registry:/var/lib/registry \
	--workdir=/var/lib/registry \
	--publish=$(LOCALPORT):5000 \
	--name $(NAME) \
	--hostname $(HOSTNAME)


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
build:                # Build Docker image
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	../bin/create-rootfs.bash bash bash2ash
	$(DOCKER_BUILD) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	rm -rf rootfs

.PHONY: run
run:                  # Run Docker container
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	$(DOCKER_RUN) --hostname $(NAME) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: version
version:              # Check version
	@$(DOCKER_RUN) $(IMAGE) registry --version 2> /dev/null | \
		sed -e "s@.* v@$(shell pwd): Registry @"

.PHONY: rmi
rmi:                  # Remove Docker image
	docker rmi -f $(IMAGE) ||:

.PHONY: rmi-base
rmi-base: rmi         # Remove Docker image including base image
	docker rmi -f $(BASE_IMAGE) ||:

.PHONY: help
help:                 # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
