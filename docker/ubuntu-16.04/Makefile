BASE_IMAGE := ubuntu:16.04
IMAGE := drtuxwang/ubuntu:16.04
DOCKER_BUILD_FLAGS ?=

BUILD_DIRS := bash dev


.PHONY: default
default: build status

.PHONY: status
status:
	@docker images | grep "^$(shell echo $(IMAGE) | sed -e 's/-.*:/:/;s/:/.* /') " ||:
	@docker images | grep "^$(shell echo $(BASE_IMAGE) | sed -e 's/-.*:/:/;s/:/  */') " ||:

.PHONY: pull
pull:
	docker pull $(BASE_IMAGE)

.PHONY: save
save:
	../bin/docker-save $(BASE_IMAGE)

.PHONY: build
build:
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	rm -rf tmpdir
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR build || exit 1; \
	done

.PHONY: run
run:
	make -C bash run

.PHONY: version
version:
	@for DIR in $(BUILD_DIRS); do \
		make --no-print-directory -C $$DIR version ||:; \
	done

.PHONY: rmi
rmi:
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR rmi; \
	done
	docker rmi -f $(IMAGE) ||:

.PHONY: rmi-base
rmi-base: rmi
	docker rmi -f $(BASE_IMAGE) ||:

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
