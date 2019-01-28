NAME := alpine
VERSION := 3.8
IMAGE := drtuxwang/$(NAME):$(VERSION)

# Docker build
BASE_IMAGE := drtuxwang/$(NAME)-base:$(VERSION)
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


default: build
	docker images

.PHONY: pull
pull:
	docker pull `grep FROM Dockerfile-base | cut -f2 -d" "`

.PHONY: build
build:
	rm -rf tmpdir
	mkdir -p tmpdir/bin tmpdir/root
	cp -p $(TOPDIR)/bin/* tmpdir/bin/
	cp -p $(TOPDIR)/config/bashrc tmpdir/root/.bashrc
	cp -p $(TOPDIR)/config/vimrc tmpdir/root/.vimrc
	docker run \
		--rm --volume=`pwd`:`pwd` \
		--workdir=`pwd` \
		--volume=`realpath $(TOPDIR)/bin`:/vol/app:ro \
		python:3 /vol/app/fmod -R *
	@echo "\n*** Building \"$(BASE_IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) -f Dockerfile-base -t $(BASE_IMAGE) .
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) -f Dockerfile -t $(IMAGE) .
	rm -rf tmpdir

.PHONY: run
run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) \
		--hostname `echo $(NAME)-$(VERSION) | sed -e "s/[.]//g"` \
		$(IMAGE) \
		$(DOCKER_RUN_COMMAND) \
		||:

.PHONY: version
version:
	@docker run $(DOCKER_RUN_FLAGS) $(IMAGE) cat /etc/alpine-release 2> /dev/null | \
		sed -e "s@^@`pwd`: Alpine Linux @"

.PHONY: clean
clean:
	docker rmi -f $(IMAGE) ||:
	docker rmi -f `grep FROM Dockerfile | cut -f2 -d" "` ||:
