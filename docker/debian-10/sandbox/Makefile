BASE_IMAGE := drtuxwang/debian:10
IMAGE := drtuxwang/debian-sandbox:10
NAME := debian-sandbox-10
HOSTNAME := debian-10

TOPDIR := ../../..
ifndef DOCKER_BUILD_FLAGS
	DOCKER_BUILD_FLAGS=
endif

ifndef LOCALPORT
	LOCALPORT=5901
endif
ifndef DOCKER_RUN_FLAGS
	DOCKER_RUN_FLAGS=--network=none --user=99999:99999
endif
DOCKER_RUN_FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-quota=1000000 \
	--cpu-shares=50000 \
	--memory=2000m \
	--memory-reservation=50m \
	--publish $(LOCALPORT):5901 \
	--name $(NAME) \
	--hostname $(HOSTNAME) \
	$(DOCKER_RUN_FLAGS)
ifndef DOCKER_RUN_COMMAND
	DOCKER_RUN_COMMAND=
endif


.PHONY: default
default: build
	docker images

.PHONY: build
build:
	mkdir -p tmpdir/bin tmpdir/etc tmpdir/home/.config/xfce4/terminal tmpdir/home/.vnc
	cp -p $(TOPDIR)/etc/install-python-requirements.sh tmpdir/etc
	cp -p $(TOPDIR)/etc/python-requirements.txt tmpdir/etc
	cp -p $(TOPDIR)/bin/* tmpdir/bin/
	cp -p $(TOPDIR)/config/docker-init tmpdir/etc
	cp -p $(TOPDIR)/config/bashrc tmpdir/home/.bashrc
	cp -p $(TOPDIR)/config/profile tmpdir/home/.profile
	cp -p $(TOPDIR)/config/terminalrc tmpdir/home/.config/xfce4/terminal
	cp -p $(TOPDIR)/config/tmux.conf tmpdir/home/.tmux.conf
	cp -p $(TOPDIR)/config/vimrc tmpdir/home/.vimrc
	cp -p files/xstartup tmpdir/home/.vnc/
	$(TOPDIR)/etc/setmod *
	tar cf tmpdir/home.tar -C tmpdir/home --owner=0 --group=0 \
		.bashrc \
		.config \
		.profile \
		.tmux.conf \
		.vimrc \
		.vnc
	chmod 644 tmpdir/home.tar
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	rm -rf tmpdir

.PHONY: run
run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: version
version:
	@docker run --entrypoint gcc $(IMAGE) --version | grep ^gcc | \
		sed -e "s/([^)]*)//" | awk '{printf("'$(shell pwd)': gcc %s\n", $$2)}'

.PHONY: push
push:
	@echo "\n*** Pushing \"$(IMAGE)\" Docker image ***"
	@docker push $(IMAGE)

.PHONY: clean
clean:
	docker rmi -f $(IMAGE) ||:
