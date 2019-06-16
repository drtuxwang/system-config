NAME := clearlinux
IMAGE := drtuxwang/$(NAME)

# Docker build
BASE_IMAGE := drtuxwang/$(NAME)-base
TOPDIR := ../..
ifndef DOCKER_BUILD_FLAGS
	DOCKER_BUILD_FLAGS=
endif

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
	docker pull $(shell grep FROM Dockerfile | cut -f2 -d" ")

.PHONY: build
build:
	rm -rf tmpdir
	mkdir -p tmpdir/bin tmpdir/root
	cp -p $(TOPDIR)/bin/* tmpdir/bin/
	cp -p $(TOPDIR)/config/bashrc tmpdir/root/.bashrc
	cp -p $(TOPDIR)/config/vimrc tmpdir/root/.vimrc
	$(TOPDIR)/etc/setmod *
	@echo "\n*** Building \"$(BASE_IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) -f Dockerfile -t $(BASE_IMAGE) .
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) -f Dockerfile-shell -t $(IMAGE) .
	rm -rf tmpdir

.PHONY: run
run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) \
		--hostname $(NAME) \
		$(IMAGE) \
		$(DOCKER_RUN_COMMAND) \
		||:

.PHONY: version
version:
	@docker run $(DOCKER_RUN_FLAGS) $(IMAGE) cat /usr/share/clear/version 2> /dev/null | awk '{print $1}' | sed -e "s@^@$(shell pwd): Clear Linux @"

.PHONY: clean
clean:
	docker rmi -f $(IMAGE) $(BASE_IMAGE) ||:
	docker rmi -f $(shell grep FROM Dockerfile | cut -f2 -d" ") ||:
