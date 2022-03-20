BASE_IMAGE := drtuxwang/ubuntu:16.04
IMAGE := drtuxwang/ubuntu-bash:16.04
NAME := ubuntu1604-bash
HOSTNAME := ubuntu1604-bash
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
	--hostname $(HOSTNAME) \
	$(DOCKER_RUN_FLAGS)


.PHONY: default
default: build status

.PHONY: status
status:       # Status of Docker images
	@make --no-print-directory -C .. status

.PHONY: build
build:        # Build Docker images
	../../bin/create-rootfs.sh bash bin-sysinfo vim
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	rm -rf rootfs

.PHONY: run
run:          # Run Docker container
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: version
version:      # Check versions
	@docker run --rm $(IMAGE) cat /etc/os-release 2> /dev/null | \
		grep "^VERSION=" | sed -e "s@.*=\"@$(shell pwd): Ubuntu Linux @;s@ (.*@@"

.PHONY: rmi
rmi:          # Remove Docker images
	docker rmi -f $(IMAGE) ||:

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
