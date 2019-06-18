NAME := ubuntu
IMAGE := drtuxwang/$(NAME)

# Docker build
SANDBOX_IMAGE := drtuxwang/$(NAME)-sandbox
TOPDIR := ../..
ifndef DOCKER_BUILD_FLAGS
	DOCKER_BUILD_FLAGS=
endif
BUILD_DIRS := bash sandbox-gcc sandbox-python sandbox-firefox sandbox-wine
TEST_DIRS := sandbox-python


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
	@echo "\n*** Building \"$(SANDBOX_IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) -f Dockerfile-sandbox -t $(SANDBOX_IMAGE) .
	rm -rf tmpdir
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR build || exit 1; \
	done

.PHONY: run
run:
	DOCKER_BUILD_FLAGS="$(DOCKER_BUILD_FLAGS)" make -C bash run

.PHONY: test
test:
	for DIR in $(TEST_DIRS); do \
		make -C $$DIR test || exit 1; \
	done

.PHONY: version
version:
	@for DIR in $(BUILD_DIRS); do \
		make --no-print-directory -C $$DIR version ||:; \
	done

.PHONY: clean
clean:
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR clean; \
	done
	docker rmi -f $(IMAGE) $(SANDBOX_IMAGE) ||:
	docker rmi -f $(shell grep FROM Dockerfile | cut -f2 -d" ") ||:
