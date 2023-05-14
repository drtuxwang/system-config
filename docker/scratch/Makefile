BASE_IMAGE := scratch
IMAGE := drtuxwang/scratch:latest
NAME := scratch-bash
HOSTNAME := scratch-bash
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
	--privileged=true \
	$(shell ls -1d /* | grep -E -v "/(proc|root)$$" | awk '{printf("--volume=%s:%s ",$$1,$$1)}') \
	--volume="/etc/hosts:/etc/hosts" \
	--volume="/etc/passwd:/etc/passwd:ro" \
	--volume="/etc/group:/etc/group:ro" \
	--name $(NAME) \
	--hostname $(shell uname -n)-$(HOSTNAME)


.PHONY: default
default: build status # Default

.PHONY: status
status:              # Status of Docker image
	@docker images --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}" | \
		grep -E "^($(shell echo $(IMAGE) | sed -e 's/:/(-.*|):/')|$(BASE_IMAGE)) " ||:

.PHONY: pull
pull:                # Pull Docker base image

.PHONY: pull-save
pull-save:           # pull Docker base image and save as tar file if changed

.PHONY: save
save:                # Save Docker base image as tar file

.PHONY: build
build:               # Build Docker images
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	../bin/create-rootfs.bash bash tmux vim
	$(DOCKER_BUILD) --build-arg BASE_IMAGE=$(BASE_IMAGE) --force-rm=true -t $(IMAGE) .
	rm -rf rootfs

.PHONY: run
run:                 # Run Docker container
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	$(DOCKER_RUN) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: version
version:             # Check versions
	@echo "$(shell pwd): scratch"

.PHONY: rmi
rmi:                 # Remove Docker images
	docker rmi -f $(IMAGE) ||:

.PHONY: rmi-base
rmi-base: rmi        # Remove Docker images including base image
	docker rmi -f $(BASE_IMAGE) ||:

.PHONY: help
help:                # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
