BASE_IMAGE := registry:2.6
IMAGE := drtuxwang/registry:2.6
NAME := registry2-server
HOSTNAME := registry2-server

TOPDIR := ../..
ifndef DOCKER_BUILD_FLAGS
	DOCKER_BUILD_FLAGS=
endif

ifndef LOCALPORT
	LOCALPORT=5000
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
	--volume=/var/lib/registry:/var/lib/registry \
	--workdir=/var/lib/registry \
	--publish=$(LOCALPORT):5000 \
	--name $(NAME) \
	--hostname $(HOSTNAME) \
	$(DOCKER_RUN_FLAGS)
ifndef DOCKER_RUN_COMMAND
	DOCKER_RUN_COMMAND=
endif


.PHONY: default
default: build status

.PHONY: status
status:
	docker images | grep "^`echo $(IMAGE) | sed -e 's/-.*:/:/;s/:/.* /'` " | sort

.PHONY: pull
pull:
	docker pull $(BASE_IMAGE)
	docker images | grep "^$(shell echo $(BASE_IMAGE) | sed -e 's/:/.* /') "

.PHONY: save
save:
	../docker-save.sh $(BASE_IMAGE)

.PHONY: build
build:
	rm -rf tmpdir
	mkdir -p tmpdir/root
	cp -p $(TOPDIR)/config/bashrc tmpdir/root/.bashrc
	$(TOPDIR)/etc/setmod *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	rm -rf tmpdir

.PHONY: run
run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) --hostname $(NAME) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: version
version:
	@docker run $(DOCKER_RUN_FLAGS) $(IMAGE) registry --version 2> /dev/null | \
		sed -e "s@.* v@$(shell pwd): Registry @"

.PHONY: rmi
rmi:

.PHONY: rmi-base
rmi-base: rmi
	docker rmi -f $(IMAGE) ||:

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
