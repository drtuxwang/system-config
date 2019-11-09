NAME := busybox-bash
IMAGE := drtuxwang/$(NAME)

# Docker build
BASE_IMAGE := drtuxwang/$(NAME)-base
TOPDIR := ../../..
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
	--memory-reservation=50m
ifndef DOCKER_RUN_COMMAND
	DOCKER_RUN_COMMAND=
endif


.PHONY: default
default: build
	docker images

.PHONY: build
build:
	rm -rf tmpdir
	mkdir -p tmpdir/bin tmpdir/root
	cp -p $(TOPDIR)/bin/sysinfo.sh tmpdir/bin/sysinfo
	cp -p $(TOPDIR)/config/bashrc tmpdir/root/.bashrc
	$(TOPDIR)/etc/setmod *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) -t $(IMAGE) .
	rm -rf tmpdir

.PHONY: run
run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) --hostname $(NAME) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: version
version:
	@docker run $(DOCKER_RUN_FLAGS) $(IMAGE) busybox 2> /dev/null | grep "^BusyBox v" | \
		sed -e "s@^BusyBox v@$(shell pwd): BusyBox @;s@ (.*@@"

.PHONY: push
push:
	@echo "\n*** Pushing \"$(IMAGE)\" Docker image ***"
	@docker push $(IMAGE)

.PHONY: push
push:
	@echo "\n*** Pushing \"$(IMAGE)\" Docker image ***"
	@docker push $(IMAGE)

.PHONY: clean
clean:
	docker rmi -f $(IMAGE) ||:
