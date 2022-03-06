BASE_IMAGE := drtuxwang/debian:11-slim
DOCKER_REPO=https://download.docker.com/linux/debian/dists/bullseye/pool/stable/amd64
DOCKER_DEB=docker-ce-cli_20.10.12~3-0~debian-bullseye_amd64.deb
IMAGE := drtuxwang/debian-docker:11-slim
NAME := debian11-docker
HOSTNAME := debian11-docker
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
	--volume /var/run/docker.sock:/var/run/docker.sock \
	--privileged=true \
	--name $(NAME) \
	--hostname $(HOSTNAME) \
	$(DOCKER_RUN_FLAGS)


.PHONY: default
default: build status

.PHONY: status
status:       # Status of Docker images
	@make --no-print-directory -C .. status

.PHONY: build
build:        # Build Docker images
	../../bin/create-root-disk.sh bash bin vim
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build \
		$(DOCKER_BUILD_FLAGS) \
		--build-arg BASE_IMAGE=$(BASE_IMAGE) \
		--build-arg DOCKER_REPO=$(DOCKER_REPO) \
		--build-arg DOCKER_DEB=$(DOCKER_DEB) \
		-t $(IMAGE) .
	rm -rf root-disk

.PHONY: run
run:          # Run Docker container
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: version
version:      # Check versions
	@docker run --rm --entrypoint docker $(IMAGE) --version 2> /dev/null | \
		grep ^Docker | sed -e "s/,/ /g" | awk '{printf("'$(shell pwd)': docker %s\n", $$3)}'

.PHONY: rmi
rmi:          # Remove Docker images
	docker rmi -f $(IMAGE) ||:

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
