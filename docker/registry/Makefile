NAME := registry
VERSION := 2.6
IMAGE := drtuxwang/$(NAME):$(VERSION)

# Docker build
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


default: build
	docker images

.PHONY: pull
pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`

.PHONY: build
build:
	rm -rf tmpdir
	mkdir -p tmpdir/bin tmpdir/config
	cp -p $(TOPDIR)/config/ash-2bash tmpdir/bin/bash
	cp -p $(TOPDIR)/config/bashrc tmpdir/config/.bashrc
	$(TOPDIR)/etc/setmod *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) -t $(IMAGE) .
	rm -rf tmpdir

.PHONY: run
run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) \
		--volume=/var/lib/registry:/var/lib/registry \
		--publish 5000:5000 \
		--hostname `echo $(NAME)-$(VERSION) | sed -e "s/[.]//g"` \
		--workdir /var/lib/registry \
		$(IMAGE) ||:

.PHONY: version
version:
	@docker run $(DOCKER_RUN_FLAGS) $(IMAGE) registry --version 2> /dev/null | sed -e "s@.* v@`pwd`: Registry @"

.PHONY: clean
clean:
	docker rmi -f $(IMAGE) ||:
	docker rmi -f `grep FROM Dockerfile | cut -f2 -d" "` ||:
