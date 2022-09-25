BASE_IMAGE := golang:1.18-alpine
IMAGE := drtuxwang/golang:1.18-alpine
NAME := golang-118-bash
HOSTNAME := golang-118-bash
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
default: build status # Default

.PHONY: status
status:              # Status of Docker image
	@docker images --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.CreatedSince}}\t{{.Size}}" | \
		grep -E "^($(shell echo $(IMAGE) | sed -e 's/:/(-.*|):/')|$(BASE_IMAGE)) " ||:

.PHONY: pull
pull:                # Pull Docker base image
	docker pull $(BASE_IMAGE)
	@make --no-print-directory status

.PHONY: pull-save
pull-save:           # Pull Docker base image and save as tar file if changed
	../bin/docker-pull-save.sh $(BASE_IMAGE)

.PHONY: save
save:                # Save Docker base image as tar file
	../bin/docker-save.sh $(BASE_IMAGE)

.PHONY: build
build:               # Build Docker images
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	../bin/create-rootfs.sh bash bin vim
	docker build $(DOCKER_BUILD_FLAGS) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	rm -rf rootfs

.PHONY: run
run:                 # Run Docker container
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: version
version:             # Check versions
	@docker run $(DOCKER_RUN_FLAGS) $(IMAGE) go version 2> /dev/null | \
		sed -e "s@.*go@$(shell pwd): Golang @"

.PHONY: rmi
rmi:                 # Remove Docker images
	docker rmi -f $(IMAGE) ||:

.PHONY: rmi-base
rmi-base: rmi        # Remove Docker images including base image
	docker rmi -f $(BASE_IMAGE) ||:

.PHONY: help
help:                # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
