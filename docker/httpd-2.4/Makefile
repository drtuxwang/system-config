BASE_IMAGE := httpd:2.4-alpine
IMAGE := drtuxwang/httpd:2.4-alpine
NAME := httpd-proxy
HOSTNAME := httpd-proxy
LOCALPORT ?= 8080
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
	--publish $(LOCALPORT):80 \
	--name $(NAME) \
	--hostname $(HOSTNAME)


.PHONY: default
default: build status # Default

.PHONY: status
status:               # Status of Docker image
	@docker images --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}" | \
		grep -E "^($(shell echo $(IMAGE) | sed -e 's/:/(-.*|):/')|$(BASE_IMAGE)) " ||:

.PHONY: pull
pull:                 # Pull Docker base image
	docker pull $(BASE_IMAGE)
	@make --no-print-directory status

.PHONY: pull-save
pull-save:            # Pull updated Docker images and save to tar archives
	../bin/pull-save.bash $(BASE_IMAGE)

.PHONY: save
save: pull            # Pull Docker base image and save to tar archive
	../../bin/docker-save $(BASE_IMAGE)

.PHONY: build
build:                # Build Docker images
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	../bin/create-rootfs.bash bash bash2ash bin-sysinfo
	$(DOCKER_BUILD) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	rm -rf rootfs

.PHONY: run
run:                  # Run Docker container
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	$(DOCKER_RUN) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: version
version:              # Check versions
	@$(DOCKER_RUN) --entrypoint /usr/local/apache2/bin/httpd $(IMAGE) -version 2>&1 | \
		grep "^Server version: Apache/" | sed -e "s@.*/@$(shell pwd): Apache @;s/ (.*//"

.PHONY: rmi
rmi:                  # Remove Docker images
	docker rmi -f $(IMAGE) ||:

.PHONY: rmi-base
rmi-base: rmi         # Remove Docker images including base image
	docker rmi -f $(BASE_IMAGE) ||:

.PHONY: help
help:                 # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
