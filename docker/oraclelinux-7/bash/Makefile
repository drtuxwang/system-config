BASE_IMAGE := drtuxwang/oraclelinux:7-slim
IMAGE := drtuxwang/oraclelinux-bash:7-slim
NAME := oraclelinux7-bash
HOSTNAME := oraclelinux7-bash
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
	../../bin/create-rootfs.sh bash bin vim
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	rm -rf rootfs

.PHONY: run
run:          # Run Docker container
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: version
version:      # Check versions
	@docker run --rm $(IMAGE) cat /etc/system-release 2> /dev/null | \
		sed -e "s@.*release @$(shell pwd): @" | awk '{printf("%s CentOS Linux %s\n", $$1, $$2)}'

.PHONY: rmi
rmi:          # Remove Docker images
	docker rmi -f $(IMAGE) ||:

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
