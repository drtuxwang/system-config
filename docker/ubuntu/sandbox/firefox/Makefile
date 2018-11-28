NAME := ubuntu-firefox-sandbox
VERSION := 18.04
IMAGE := drtuxwang/$(NAME):$(VERSION)
TOPDIR := ../../../..

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
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	mkdir -p tmpdir/home/.mozilla/firefox
	cp -p profiles.ini tmpdir/home/.mozilla/firefox
	cp -rp $(FIREFOX_PROFILE) tmpdir/home/.mozilla/firefox/sandbox
	cp -p user.js tmpdir/home/.mozilla/firefox/sandbox/
	tar cf tmpdir/home-firefox.tar -C tmpdir/home --owner=0 --group=0 .mozilla
	chmod 644 tmpdir/home-firefox.tar
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
		|| exit 0

.PHONY: clean
clean:
	docker rmi -f $(IMAGE) ||:
