BASE_IMAGE := python:3.10-slim-bullseye
IMAGE := drtuxwang/python:3.10-slim-bullseye
DOCKER_BUILD_FLAGS ?=

BUILD_DIRS := bash dev devpi full


.PHONY: default
default: build status # Default

.PHONY: status
status:              # Status of Docker image
	@docker images --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}" | \
		grep -E "^($(shell echo $(IMAGE) | sed -e 's/:/(-.*|):/')|$(BASE_IMAGE)) " ||:

.PHONY: pull
pull:                # Pull Docker base image
	docker pull $(BASE_IMAGE)
	@make --no-print-directory status

.PHONY: pull-save
pull-save:           # pull Docker base image and save as tar file if changed
	../bin/docker-pull-save.bash $(BASE_IMAGE)

.PHONY: save
save:                # Save Docker base image as tar file
	../bin/docker-save.bash $(BASE_IMAGE)

.PHONY: build
build:               # Build Docker images
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	for DIR in $(BUILD_DIRS); do \
		make --no-print-directory --directory $$DIR build || exit 1; \
	done

.PHONY: test
test:                # Run tests
	make --no-print-directory --directory dev test

.PHONY: run
run:                 # Run Docker container
	make --no-print-directory --directory bash run

.PHONY: version
version:             # Check versions
	@for DIR in $(BUILD_DIRS); do \
		make --no-print-directory --directory $$DIR version || exit 1; \
	done

.PHONY: rmi
rmi:                 # Remove Docker images
	for DIR in $(BUILD_DIRS); do \
		make --no-print-directory --directory $$DIR rmi; \
	done
	docker rmi -f $(IMAGE) ||:

.PHONY: rmi-base
rmi-base: rmi        # Remove Docker images including base image
	docker rmi -f $(BASE_IMAGE) ||:

.PHONY: help
help:                # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
