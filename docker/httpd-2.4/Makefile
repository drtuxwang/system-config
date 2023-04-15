BASE_IMAGE := httpd:2.4-alpine
IMAGE := drtuxwang/httpd:2.4-alpine
NAME := httpd-proxy
HOSTNAME := httpd-proxy
LOCALPORT ?= 8080
DOCKER_BUILD_FLAGS ?=
DOCKER_RUN_FLAGS ?=

DOCKER_RUN_FLAGS := \
	--rm \
	--interactive \
	--tty \
	--cpu-quota=1000000 \
	--cpu-shares=50000 \
	--memory=1000m \
	--memory-reservation=50m \
	--publish $(LOCALPORT):80 \
	--name $(NAME) \
	--hostname $(HOSTNAME) \
	$(DOCKER_RUN_FLAGS)


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
pull-save:           # Pull Docker base image and save as tar file if changed
	../bin/docker-pull-save.bash $(BASE_IMAGE)

.PHONY: save
save:                # Save Docker base image as tar file
	../bin/docker-save.bash $(BASE_IMAGE)

.PHONY: build
build:               # Build Docker images
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	../bin/create-rootfs.bash bash bash2ash bin-sysinfo
	docker build $(DOCKER_BUILD_FLAGS) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	rm -rf rootfs

.PHONY: run
run:                 # Run Docker container
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: version
version:             # Check versions
	@docker run $(DOCKER_RUN_FLAGS) --entrypoint /usr/local/apache2/bin/httpd $(IMAGE) -version 2>&1 | \
		grep "^Server version: Apache/" | sed -e "s@.*/@$(shell pwd): Apache @;s/ (.*//"

.PHONY: rmi
rmi:                 # Remove Docker images
	docker rmi -f $(IMAGE) ||:

.PHONY: rmi-base
rmi-base: rmi        # Remove Docker images including base image
	docker rmi -f $(BASE_IMAGE) ||:

.PHONY: help
help:                # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
