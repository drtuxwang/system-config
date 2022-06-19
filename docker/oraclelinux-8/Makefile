BASE_IMAGE := oraclelinux:8-slim
IMAGE := drtuxwang/oraclelinux:8-slim
DOCKER_BUILD_FLAGS ?=

BUILD_DIRS := bash dev


.PHONY: default
default: build status # Default

.PHONY: status
status:              # Status of Docker image
	@docker images --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.CreatedSince}}\t{{.Size}}" | \
		egrep "^($(shell echo $(IMAGE) | sed -e 's/:/(-.*|):/')|$(BASE_IMAGE)) " ||:

.PHONY: pull
pull:                # Pull Docker base image
	docker pull $(BASE_IMAGE)
	@make --no-print-directory status

.PHONY: save
save:                # Save Docker base image as tar file
	../bin/docker-save.sh $(BASE_IMAGE)

.PHONY: build
build:               # Build Docker images
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	for DIR in $(BUILD_DIRS); do \
		make --no-print-directory -C $$DIR build || exit 1; \
	done

.PHONY: run
run:                 # Run Docker container
	make --no-print-directory -C bash run

.PHONY: version
version:             # Check versions
	@for DIR in $(BUILD_DIRS); do \
		make --no-print-directory -C $$DIR version ||:; \
	done

.PHONY: rmi
rmi:                 # Remove Docker images
	for DIR in $(BUILD_DIRS); do \
		make --no-print-directory -C $$DIR rmi; \
	done
	docker rmi -f $(IMAGE) ||:

.PHONY: rmi-base
rmi-base: rmi        # Remove Docker images including base image
	docker rmi -f $(BASE_IMAGE) ||:

.PHONY: help
help:                # Show Makefile options
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
