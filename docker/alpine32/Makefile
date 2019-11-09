NAME := alpine32
IMAGE := drtuxwang/$(NAME)

# Docker build
TOPDIR := ../..
ifndef DOCKER_BUILD_FLAGS
	DOCKER_BUILD_FLAGS=
endif
BUILD_DIRS := bash dev


.PHONY: default
default: build
	docker images

.PHONY: pull
pull:
	docker pull $(shell grep FROM Dockerfile | cut -f2 -d" ")

.PHONY: build
build:
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) -t $(IMAGE) .
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR build || exit 1; \
	done

.PHONY: run
run:
	DOCKER_BUILD_FLAGS="$(DOCKER_BUILD_FLAGS)" make -C bash run

.PHONY: version
version:
	@for DIR in $(BUILD_DIRS); do \
		make --no-print-directory -C $$DIR version || exit 1; \
	done

.PHONY: push
push:
	@echo "\n*** Pushing \"$(IMAGE)\" Docker image ***"
	@docker push $(IMAGE)
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR push || exit 1; \
	done

.PHONY: clean
clean:
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR clean; \
	done
	docker rmi -f $(IMAGE) ||:
	docker rmi -f $(shell grep FROM Dockerfile | cut -f2 -d" ") ||:
