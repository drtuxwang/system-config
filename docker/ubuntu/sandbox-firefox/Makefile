NAME := ubuntu-firefox
VERSION := 18.04
IMAGE := drtuxwang/$(NAME):$(VERSION)
TOPDIR := ../../..

FIREFOX_PROFILE=$(HOME)/.mozilla/firefox/sandbox


ifndef FLAGS
	FLAGS=--network none
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
	mkdir -p tmpdir/bin tmpdir/etc tmpdir/home/.mozilla/firefox
	cp -p $(TOPDIR)/bin/* tmpdir/bin/
	cp -p $(TOPDIR)/config/docker-init tmpdir/etc
	cp -p $(TOPDIR)/config/bashrc tmpdir/home/.bashrc
	cp -p $(TOPDIR)/config/profile tmpdir/home/.profile
	cp -p $(TOPDIR)/config/tmux.conf tmpdir/home/.tmux.conf
	cp -p $(TOPDIR)/config/vimrc tmpdir/home/.vimrc
	cp -p profiles.ini tmpdir/home/.mozilla/firefox
	cp -rp $(FIREFOX_PROFILE) tmpdir/home/.mozilla/firefox/sandbox
	cp -p user.js tmpdir/home/.mozilla/firefox/sandbox/
	$(TOPDIR)/bin/fmod -R *
	tar cf tmpdir/home.tar -C tmpdir/home --owner=0 --group=0 \
		.bashrc \
		.profile \
		.tmux.conf \
		.vimrc \
		.mozilla
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
	@docker run --entrypoint firefox $(IMAGE) -v | grep Firefox | \
		awk '{printf("'`pwd`': firefox %s\n", $$NF)}'

.PHONY: clean
clean:
	docker rmi -f $(IMAGE) ||:
