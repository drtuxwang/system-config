BASE_IMAGE := scratch
IMAGE := drtuxwang/sudo:stable
NAME := sudo-bash
HOSTNAME := sudo-bash
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
	--privileged=true \
	$(shell ls -1d /* | egrep -v "/(proc|root)$$" | awk '{printf("--volume=%s:%s ",$$1,$$1)}') \
	--volume="/etc/hosts:/etc/hosts" \
	--volume="/etc/passwd:/etc/passwd:ro" \
	--volume="/etc/group:/etc/group:ro" \
	--name $(NAME) \
	--hostname $(shell uname -n)-$(HOSTNAME) \
	$(DOCKER_RUN_FLAGS)


.PHONY: default
default: build status

.PHONY: status
status:       # Status of Docker images
	@docker images | grep "^$(shell echo $(IMAGE) | sed -e 's/-.*:/:/;s/:/.* /') " ||:
	@docker images | grep "^$(shell echo $(BASE_IMAGE) | sed -e 's/-.*:/:/;s/:/  */') " ||:

.PHONY: pull
pull:         # Pull Docker base image

.PHONY: save
save:         # Save Docker base image as tar file

.PHONY: build
build:        # Build Docker images
	../bin/create-root-tar.sh bash tmux vim
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) --build-arg BASE_IMAGE=$(BASE_IMAGE) --force-rm=true -t $(IMAGE) .
	rm -rf tmpdir

.PHONY: run
run:          # Run Docker container
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: version
version:      # Check versions
	@echo "$(shell pwd): scratch"

.PHONY: rmi
rmi:          # Remove Docker images
	docker rmi -f $(IMAGE) ||:

.PHONY: rmi-base
rmi-base: rmi # Remove Docker images including base image
	docker rmi -f $(BASE_IMAGE) ||:

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
