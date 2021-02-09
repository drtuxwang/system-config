BASE_IMAGE := scratch
IMAGE := drtuxwang/sudo
NAME := sudo-bash
HOSTNAME := sudo-bash

TOPDIR := ../..
ifndef DOCKER_BUILD_FLAGS
	DOCKER_BUILD_FLAGS=
endif

ifndef DOCKER_RUN_FLAGS
	DOCKER_RUN_FLAGS=
endif
DOCKER_RUN_FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-quota=1000000 \
	--cpu-shares=50000 \
	--memory=1000m \
	--memory-reservation=50m \
	--privileged=true \
	$(shell ls -1d /* | egrep -v "/(proc|root)$$" | awk '{printf("--volume=%s:%s ",$$1,$$1)}') \
	--volume="/etc/hosts:/etc/hosts" \
	--volume="/etc/passwd:/etc/passwd:ro" \
	--volume="/etc/group:/etc/group:ro" \
	--name $(NAME) \
	--hostname $(shell uname -n)-$(HOSTNAME) \
	$(DOCKER_RUN_FLAGS)
ifndef DOCKER_RUN_COMMAND
	DOCKER_RUN_COMMAND=
endif


.PHONY: default
default: build status

.PHONY: status
status:
	docker images | grep "^$(shell echo $(IMAGE) | sed -e 's/-.*:/:/;s/:/.* /') " | sort

.PHONY: pull
pull:

.PHONY: build
build:
	rm -rf tmpdir
	mkdir -p tmpdir/root
	cp -p $(TOPDIR)/config/profile tmpdir/root/.profile
	cp -p $(TOPDIR)/config/vimrc tmpdir/root/.vimrc
	cp -p $(TOPDIR)/config/tmux.conf tmpdir/root/.tmux.conf
	$(TOPDIR)/etc/setmod *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) --build-arg BASE_IMAGE=$(BASE_IMAGE) --force-rm=true -t $(IMAGE) .
	rm -rf tmpdir

.PHONY: run
run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: version
version:
	@echo "$(shell pwd): scratch"

.PHONY: push
push:
	@echo "\n*** Pushing \"$(IMAGE)\" Docker image ***"
	@docker push $(IMAGE)

.PHONY: save
save:

.PHONY: rmi
rmi:

.PHONY: rmi-base
rmi-base: rmi
	docker rmi -f $(IMAGE) ||:

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
