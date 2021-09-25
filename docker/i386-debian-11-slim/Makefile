BASE_IMAGE := i386/debian:11-slim
IMAGE := drtuxwang/i386-debian:11-slim
DOCKER_BUILD_FLAGS ?=

BUILD_DIRS := bash dev


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
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR build || exit 1; \
	done

.PHONY: run
run:          # Run Docker container
	make -C bash run

.PHONY: version
version:      # Check versions
	@for DIR in $(BUILD_DIRS); do \
		make --no-print-directory -C $$DIR version ||:; \
	done

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
