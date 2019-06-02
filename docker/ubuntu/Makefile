NAME := ubuntu
IMAGE := drtuxwang/$(NAME)

# Docker build
BASE_IMAGE := drtuxwang/$(NAME)-base
SANDBOX_IMAGE := drtuxwang/$(NAME)-sandbox
TOPDIR := ../..
ifndef DOCKER_BUILD_FLAGS
	DOCKER_BUILD_FLAGS=
endif
BUILD_DIRS := devpi docker nginx sandbox-gcc sandbox-python sandbox-firefox sandbox-wine
TEST_DIRS := sandbox-python

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
	DOCKER_RUN_COMMAND=
endif


.PHONY: default
default: build
	docker images

.PHONY: pull
pull:
	docker pull $(shell grep FROM Dockerfile-base | cut -f2 -d" ")

.PHONY: build
build:
	rm -rf tmpdir
	mkdir -p tmpdir/bin tmpdir/root
	cp -p $(TOPDIR)/bin/* tmpdir/bin/
	cp -p $(TOPDIR)/config/bashrc tmpdir/root/.bashrc
	cp -p $(TOPDIR)/config/vimrc tmpdir/root/.vimrc
	$(TOPDIR)/etc/setmod *
	@echo "\n*** Building \"$(BASE_IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) -f Dockerfile-base -t $(BASE_IMAGE) .
	@echo "\n*** Building \"$(SANDBOX_IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) -f Dockerfile-sandbox -t $(SANDBOX_IMAGE) .
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) -f Dockerfile -t $(IMAGE) .
	rm -rf tmpdir
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR build || exit 1; \
	done

.PHONY: run
run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) \
		--hostname $(NAME) \
		$(IMAGE) \
		$(DOCKER_RUN_COMMAND) \
		||:

.PHONY: test
test:
	for DIR in $(TEST_DIRS); do \
		make -C $$DIR test || exit 1; \
	done

.PHONY: version
version:
	@docker run $(DOCKER_RUN_FLAGS) $(IMAGE) cat /etc/os-release 2> /dev/null | \
		grep "^VERSION=" | sed -e "s@.*=\"@$(shell pwd): Ubuntu Linux @;s@ (.*@@"
	@for DIR in $(BUILD_DIRS); do \
		make --no-print-directory -C $$DIR version ||:; \
	done

.PHONY: clean
clean:
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR clean; \
	done
	docker rmi -f $(IMAGE) $(SANDBOX_IMAGE) $(BASE_IMAGE) ||:
	docker rmi -f $(shell grep FROM Dockerfile-base | cut -f2 -d" ") ||:
