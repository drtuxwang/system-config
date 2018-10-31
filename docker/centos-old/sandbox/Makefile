NAME := centos-sandbox
VERSION := 6
IMAGE := drtuxwang/$(NAME):$(VERSION)
TOPDIR := ../../..

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

# PHONY targets
.PHONY: pull build run clean

default: build
	docker images

pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`

build:
	rm -rf tmpdir
	mkdir -p tmpdir/bin tmpdir/etc tmpdir/root
	cp -p $(TOPDIR)/bin/* tmpdir/bin/
	cp -p $(TOPDIR)/config/docker-xinit tmpdir/etc
	cp -p $(TOPDIR)/config/bashrc tmpdir/root/.bashrc
	cp -p $(TOPDIR)/config/profile tmpdir/root/.profile
	cp -p $(TOPDIR)/config/tmux.conf tmpdir/root/.tmux.conf
	cp -p $(TOPDIR)/config/vimrc tmpdir/root/.vimrc
	$(TOPDIR)/bin/fmod -R *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -f Dockerfile -t $(IMAGE) .
	rm -rf tmpdir

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) --hostname $(NAME) $(IMAGE) $(COMMAND) || exit 0

clean:
	docker rmi -f $(IMAGE) ||:
	docker rmi -f `grep FROM Dockerfile | cut -f2 -d" "` ||:
