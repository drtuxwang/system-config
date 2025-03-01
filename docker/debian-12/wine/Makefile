BASE_IMAGE := debian:12-slim
IMAGE := drtuxwang/debian-wine:12-slim
NAME := debian12-wine
HOSTNAME := debian12-wine
DOCKER_BUILD := docker buildx build $(DOCKER_BUILD_FLAGS)
ifeq ($(shell docker --help | grep -c buildx), 0)
	DOCKER_BUILD := docker build
endif
DOCKER_RUN := docker run \
	--rm \
	--interactive \
	--tty \
	--cpu-quota=1000000 \
	--cpu-shares=50000 \
	--memory=2000m \
	--memory-reservation=50m \
	--publish $(LOCALPORT):22 \
	--name $(NAME) \
	--hostname $(HOSTNAME) \
	--env="DISPLAY" \
	--volume="/tmp/.X11-unix:/tmp/.X11-unix" \
	--volume="$(HOME)/.Xauthority:/root/.Xauthority:rw" \
	$(DOCKER_RUN_FLAGS)
ifdef http_proxy
	DOCKER_BUILD := $(DOCKER_BUILD) \
		--build-arg http_proxy=$(http_proxy) \
		--build-arg https_proxy=$(https_proxy) \
		--build-arg no_proxy=$(no_proxy)
	DOCKER_RUN := $(DOCKER_RUN) \
		--env http_proxy=$(http_proxy) \
		--env https_proxy=$(https_proxy) \
		--env no_proxy=$(no_proxy)
endif


.PHONY: default
default: build status # Default

.PHONY: status
status:               # Status of Docker images
	@make --no-print-directory --directory .. status

.PHONY: build
build:                # Build Docker images
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	$(DOCKER_BUILD) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .

.PHONY: build-no-cache
build-no-cache:       # Build Docker image with no cache
	@DOCKER_BUILD_FLAGS="--no-cache" make --no-print-directory build

.PHONY: run
run:                  # Run Docker container
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	xhost +SI:localuser:root
	$(DOCKER_RUN) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: version
version:              # Check versions
	@docker run --rm --entrypoint dpkg $(IMAGE) -s xfce4 | \
		awk '/^Version: / {printf("'$(shell pwd)': Xfce %s\n", $$2)}'

.PHONY: rmi
rmi:                  # Remove Docker images
	docker rmi -f $(IMAGE) ||:

.PHONY: help
help:                 # Show Makefile options
	@grep "^[A-Za-z0-9].*:" $(lastword $(MAKEFILE_LIST))
