BASE_IMAGE := busybox:1.36
IMAGE := drtuxwang/busybox:1.36
NAME := busybox136
HOSTNAME := busybox136
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
	--hostname $(HOSTNAME)


.PHONY: default
default: build status # Default

.PHONY: status
status:               # Status of Docker images
	@docker images --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}" | grep "^$(BASE_IMAGE) " ||:
	@docker images --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}" | grep "^$(IMAGE) " ||:

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
	../bin/create-rootfs.bash bash bash2ash bin-sysinfo vim
	$(DOCKER_BUILD) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	rm -rf rootfs

.PHONY: run
run:                  # Run Docker container
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	$(DOCKER_RUN) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: version
version:              # Check version
	@docker run --rm $(IMAGE) busybox 2> /dev/null | grep "^BusyBox v" | \
		sed -e "s@^BusyBox v@$(shell pwd): BusyBox @;s@ (.*@@"

.PHONY: rmi
rmi:                  # Remove Docker image
	docker rmi -f $(IMAGE) ||:

.PHONY: rmi-base
rmi-base: rmi         # Remove Docker image including base image
	docker rmi -f $(BASE_IMAGE) ||:

.PHONY: help
help:                 # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
