BASE_IMAGE := docker:20.10
IMAGE := drtuxwang/docker:20.10
NAME := docker-bash
HOSTNAME := docker-bash
DOCKER_BUILD_FLAGS ?=
DOCKER_RUN_FLAGS ?=
DOCKER_RUN_COMMAND ?=

BUILD_DIRS :=
DOCKER_RUN_FLAGS := \
	--rm \
	--interactive \
	--tty \
	--cpu-quota=1000000 \
	--cpu-shares=50000 \
	--memory=1000m \
	--memory-reservation=50m \
	--volume=/etc/passwd:/etc/passwd:ro \
	--volume=/etc/group:/etc/group:ro \
	--volume=/shared:/shared \
	--volume /var/run/docker.sock:/var/run/docker.sock \
	--env TERM=$(TERM) \
	--env USER=$(USER) \
	--privileged=true \
	--name $(NAME) \
	--hostname $(HOSTNAME) \
	$(DOCKER_RUN_FLAGS)


.PHONY: default
default: build status

.PHONY: status
status:       # Status of Docker images
	@docker images | grep "^$(shell echo $(IMAGE) | sed -e 's/-.*:/:/;s/:/.* /') " ||:
	@docker images | grep "^$(shell echo $(BASE_IMAGE) | sed -e 's/-.*:/:/;s/:/  */') " ||:

.PHONY: pull
pull:         # Pull Docker base image
	docker pull $(BASE_IMAGE)
	docker images | grep "^$(shell echo $(BASE_IMAGE) | sed -e 's/:/.* /') "

.PHONY: save
save:         # Save Docker base image as tar file
	../bin/docker-save.sh $(BASE_IMAGE)

.PHONY: build
build:        # Build Docker images
	../bin/create-root-tar.sh bash bash2ash bin-sysinfo
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	rm -rf tmpdir

.PHONY: run
run:          # Run Docker container
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: version
version:      # Check versions
	@docker run $(DOCKER_RUN_FLAGS) --entrypoint docker $(IMAGE) --version 2> /dev/null | grep ^Docker | \
		sed -e "s/,/ /g" | awk '{printf("'$(shell pwd)': docker %s\n", $$3)}'

.PHONY: rmi
rmi:          # Remove Docker images
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR rmi; \
	done
	docker rmi -f $(IMAGE) ||:

.PHONY: rmi-base
rmi-base: rmi # Remove Docker images including base image
	docker rmi -f $(BASE_IMAGE) ||:

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
