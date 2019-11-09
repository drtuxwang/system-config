NAME := python
IMAGE := drtuxwang/$(NAME)

# Docker build
TOPDIR := ../..
ifndef DOCKER_BUILD_FLAGS
	DOCKER_BUILD_FLAGS=
endif
BUILD_DIRS := bash devpi

# Docker run
DOCKER_RUN_FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-quota=1000000 \
	--cpu-shares=50000 \
	--memory=1000m \
	--memory-reservation=50m \
	--volume=/shared:/shared
ifndef DOCKER_RUN_COMMAND
	DOCKER_RUN_COMMAND=python3
endif


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

.PHONY: test
test:
	make -C bash test

.PHONY: run
run:
	DOCKER_BUILD_FLAGS="$(DOCKER_RUN_FLAGS)" make -C bash run

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
	docker rmi -f $(IMAGE) $(BASE_IMAGE) ||:
