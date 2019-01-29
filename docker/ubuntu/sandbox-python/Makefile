NAME := ubuntu-python
VERSION := 18.04
IMAGE := drtuxwang/$(NAME):$(VERSION)

# Docker build
TOPDIR := ../../..
ifndef DOCKER_BUILD_FLAGS
	DOCKER_BUILD_FLAGS=
endif

# Docker run
ifndef DOCKER_RUN_FLAGS
	DOCKER_RUN_FLAGS=--network none --user=99999:99999
endif
DOCKER_RUN_FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-quota=1000000 \
	--cpu-shares=50000 \
	--memory=2000m \
	--memory-reservation=50m \
	--volume=/shared:/shared \
	$(DOCKER_RUN_FLAGS)
ifndef DOCKER_RUN_COMMAND
	DOCKER_RUN_COMMAND=
endif


default: build
	docker images

.PHONY: pull
pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`

.PHONY: build
build:
	rm -rf tmpdir
	mkdir -p tmpdir/bin tmpdir/etc tmpdir/home
	cp -p $(TOPDIR)/etc/install-python-requirements.sh tmpdir/etc
	cp -p $(TOPDIR)/etc/python-requirements.txt tmpdir/etc
	cp -p $(TOPDIR)/bin/* tmpdir/bin/
	cp -p $(TOPDIR)/config/docker-init tmpdir/etc
	cp -p $(TOPDIR)/config/bashrc tmpdir/home/.bashrc
	cp -p $(TOPDIR)/config/profile tmpdir/home/.profile
	cp -p $(TOPDIR)/config/tmux.conf tmpdir/home/.tmux.conf
	cp -p $(TOPDIR)/config/vimrc tmpdir/home/.vimrc
	$(TOPDIR)/etc/setmod *
	tar cf tmpdir/home.tar -C tmpdir/home --owner=0 --group=0 .bashrc .profile .tmux.conf .vimrc
	chmod 644 tmpdir/home.tar
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) -f Dockerfile -t $(IMAGE) .
	rm -rf tmpdir

.PHONY: test
test:
	docker run \
		--rm \
		--volume=`realpath $(TOPDIR)`:/vol/app:ro \
		--workdir=/vol/app \
		$(IMAGE) \
		find -type f ./

	docker run \
		--rm \
		--volume=`realpath $(TOPDIR)`:/vol/app:ro \
		--workdir=/vol/app \
		$(IMAGE) \
		make install test

.PHONY: run
run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) \
		--hostname `echo $(NAME) | sed -e "s/-/-$(VERSION)-/;s/[.]//g"` \
		$(IMAGE) \
		$(DOCKER_RUN_COMMAND) \
		||:

.PHONY: version
version:
	@docker run --entrypoint gcc $(IMAGE) --version | grep ^gcc | \
		sed -e "s/([^)]*)//" | awk '{printf("'`pwd`': gcc %s\n", $$2)}'

.PHONY: clean
clean:
	docker rmi -f $(IMAGE) ||:
