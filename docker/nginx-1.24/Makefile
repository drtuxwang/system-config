BASE_IMAGE := nginx:1.24.0-bullseye
IMAGE := drtuxwang/nginx-proxy:1.24.0-bullseye
NAME := nginx124-proxy
HOSTNAME := nginx124-proxy
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
status:               # Status of Docker images
	@../../bin/docker-images ^$(BASE_IMAGE) `echo $(IMAGE) | sed -e "s/-[^-:]*:/.*:/"` ||:

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
	../bin/create-rootfs.bash bash bash2ash bin-sysinfo
	$(DOCKER_BUILD) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	rm -rf rootfs

.PHONY: push-stable
push-stable:          # Tag and push stable Docker image
	docker tag ${IMAGE} `echo ${IMAGE} | sed -e "s/:.*/:stable/"`
	docker push ${IMAGE}
	docker push `echo ${IMAGE} | sed -e "s/:.*/:stable/"`

.PHONY: pull-stable
pull-stable:          # Pull stable Docker image
	docker pull ${IMAGE}
	docker pull `echo ${IMAGE} | sed -e "s/:.*/:stable/"`

.PHONY: run
run:                  # Run Docker container
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	$(DOCKER_RUN) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: version
version:              # Check version
	@$(DOCKER_RUN) $(IMAGE) -v 2>&1 | grep "^nginx version:" | \
		sed -e "s@.*/@$(shell pwd): Nginx @"

.PHONY: rmi
rmi:                  # Remove Docker image
	docker rmi -f $(IMAGE) ||:

.PHONY: rmi-base
rmi-base: rmi         # Remove Docker image including base image
	docker rmi -f $(BASE_IMAGE) ||:

.PHONY: help
help:                 # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
