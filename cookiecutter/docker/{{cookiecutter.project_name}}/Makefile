BASE_IMAGE := {{ cookiecutter.base_image_repository }}:{{ cookiecutter.base_image_tag }}
IMAGE := {{ cookiecutter.image_name }}
NAME := {{ cookiecutter.name }}
HOSTNAME := {{ cookiecutter.hostname }}
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
	--name $(NAME) \
	--hostname $(HOSTNAME) \
	$(DOCKER_RUN_FLAGS)


.PHONY: default
default: build status # Default

.PHONY: status
status:               # Status of Docker images
	docker images | grep "^$(shell echo $(IMAGE) | sed -e 's/-.*:/:/;s/:/.* /') " | sort

.PHONY: pull
pull:                 # Pull Docker base image
	docker pull $(BASE_IMAGE)
	docker images | grep "^$(shell echo $(BASE_IMAGE) | sed -e 's/:/.* /') "

.PHONY: save
save:                 # Save Docker base image as tar file
	../bin/docker-save.bash $(BASE_IMAGE)

.PHONY: build
build:                # Build Docker images
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	rm -rf tmpdir

.PHONY: run
run:                  # Run Docker container
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: version
version:              # Check versions

.PHONY: rmi
rmi:                  # Remove Docker images
	docker rmi -f $(IMAGE) ||:

.PHONY: rmi-base
rmi-base: rmi         # Remove Docker images including base image
	docker rmi -f $(BASE_IMAGE) ||:

.PHONY: help
help:                 # Show Makefile options
	@grep "^[A-Za-z0-9].*:" $(lastword $(MAKEFILE_LIST))
