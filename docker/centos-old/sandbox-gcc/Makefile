NAME := centos-gcc
VERSION := 6
IMAGE := drtuxwang/$(NAME):$(VERSION)
TOPDIR := ../../..

ifndef FLAGS
	FLAGS=--network none --user=99999:99999
endif
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-quota=1000000 \
	--cpu-shares=50000 \
	--memory=2000m \
	--memory-reservation=50m \
	--volume=/shared:/shared \
	$(FLAGS)
ifndef COMMAND
	COMMAND=
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
	cp -p $(TOPDIR)/bin/* tmpdir/bin/
	cp -p $(TOPDIR)/config/docker-init tmpdir/etc
	cp -p $(TOPDIR)/config/bashrc tmpdir/home/.bashrc
	cp -p $(TOPDIR)/config/profile tmpdir/home/.profile
	cp -p $(TOPDIR)/config/tmux.conf tmpdir/home/.tmux.conf
	cp -p $(TOPDIR)/config/vimrc tmpdir/home/.vimrc
	$(TOPDIR)/bin/fmod -R *
	tar cf tmpdir/home.tar -C tmpdir/home --owner=0 --group=0 .bashrc .profile .tmux.conf .vimrc
	chmod 644 tmpdir/home.tar

	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -f Dockerfile -t $(IMAGE) .
	rm -rf tmpdir

.PHONY: run
run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) \
		--hostname `echo $(NAME) | sed -e "s/-/-$(VERSION)-/;s/[.]//g"` \
		$(IMAGE) \
		$(COMMAND) \
		||:

.PHONY: version
version:
	@docker run --entrypoint gcc $(IMAGE) --version | grep ^gcc | \
		sed -e "s/([^)]*)//" | awk '{printf("'`pwd`': gcc %s\n", $$2)}'

.PHONY: clean
clean:
	docker rmi -f $(IMAGE) ||:
