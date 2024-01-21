BASE_IMAGE := drtuxwang/debian:12-slim
IMAGE := drtuxwang/debian-docker:12-slim
DOCKER_REPO=https://download.docker.com/linux/debian/dists/bookworm/pool/stable/amd64
DOCKER_DEB=docker-ce-cli_23.0.6-1~debian.12~bookworm_amd64.deb
NAME := debian12-docker
HOSTNAME := debian12-docker
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
	--volume /var/run/docker.sock:/var/run/docker.sock \
	--privileged=true \
	--name $(NAME) \
	--hostname $(HOSTNAME)


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

.PHONY: push-stable
push-stable:          # Tag and push stable Docker images
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
version:              # Check versions
	@docker run --rm --entrypoint docker $(IMAGE) --version 2> /dev/null | \
		grep ^Docker | sed -e "s/,/ /g" | awk '{printf("'$(shell pwd)': docker %s\n", $$3)}'

.PHONY: rmi
rmi:                  # Remove Docker images
	docker rmi -f $(IMAGE) ||:

.PHONY: help
help:                 # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
