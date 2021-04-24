BASE_IMAGE := nginx:1.16-alpine
IMAGE := drtuxwang/nginx:1.16-alpine
NAME := nginx-proxy
HOSTNAME := nginx-proxy
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
default: build status

.PHONY: status
status:
	@docker images | grep "^$(shell echo $(IMAGE) | sed -e 's/-.*:/:/;s/:/.* /') " ||:
	@docker images | grep "^$(shell echo $(BASE_IMAGE) | sed -e 's/-.*:/:/;s/:/  */') " ||:

.PHONY: pull
pull:
	docker pull $(BASE_IMAGE)
	docker images | grep "^$(shell echo $(BASE_IMAGE) | sed -e 's/:/.* /') "

.PHONY: save
save:
	../bin/docker-save $(BASE_IMAGE)

.PHONY: build
build:
	../bin/create-root-tar bash bash2ash bin-sysinfo
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	rm -rf tmpdir

.PHONY: run
run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: version
version:
	@docker run $(DOCKER_RUN_FLAGS) $(IMAGE) -v 2>&1 | grep "^nginx version:" | \
		sed -e "s@.*/@$(shell pwd): Nginx @"

.PHONY: rmi
rmi:
	docker rmi -f $(IMAGE) ||:

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
