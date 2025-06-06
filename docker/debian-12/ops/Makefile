BASE_IMAGE := debian:12-slim
IMAGE := drtuxwang/debian-ops:12-slim
DOCKER_REPO=https://download.docker.com/linux/debian/dists/bookworm/pool/stable/amd64
DOCKER_DEB=docker-ce-cli_26.1.4-1~debian.12~bookworm_amd64.deb
NAME := debian12-ops
HOSTNAME := debian12-ops
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
	--memory=1000m \
	--memory-reservation=50m \
	--volume /var/run/docker.sock:/var/run/docker.sock \
	--privileged=true \
	--name $(NAME) \
	--hostname $(HOSTNAME) \
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
	../../bin/create-rootfs.bash bash bin vim
	$(DOCKER_BUILD) \
		$(DOCKER_BUILD_FLAGS) \
		--build-arg BASE_IMAGE=$(BASE_IMAGE) \
		--build-arg DOCKER_REPO=$(DOCKER_REPO) \
		--build-arg DOCKER_DEB=$(DOCKER_DEB) \
		-t $(IMAGE) .
	rm -rf rootfs

.PHONY: build-no-cache
build-no-cache:       # Build Docker image with no cache
	@DOCKER_BUILD_FLAGS="--no-cache" make --no-print-directory build

.PHONY: push-stable
push-stable:          # Tag and push stable Docker images
	../../../bin/docker-tag ${IMAGE} `echo ${IMAGE} | sed -e "s/:.*/:stable/"`
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
version:              # Check versions
	@docker run --rm --entrypoint docker $(IMAGE) --version 2> /dev/null | \
		grep ^Docker | sed -e "s/,/ /g" | awk '{printf("'$(shell pwd)': docker %s\n", $$3)}'

.PHONY: rmi
rmi:                  # Remove Docker images
	docker rmi -f $(IMAGE) ||:

.PHONY: help
help:                 # Show Makefile options
	@grep "^[A-Za-z0-9].*:" $(lastword $(MAKEFILE_LIST))
