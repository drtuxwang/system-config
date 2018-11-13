NAME := ubuntu-wine
VERSION := 18.04
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

default: build
	docker images

.PHONY: pull
pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`

.PHONY: build
build:
	rm -rf tmpdir
	mkdir -p tmpdir/bin tmpdir/config tmpdir/etc
	cp -p $(TOPDIR)/bin/* tmpdir/bin/
	cp -p $(TOPDIR)/config/bashrc tmpdir/config/.bashrc
	cp -p $(TOPDIR)/config/docker-xinit tmpdir/config/
	cp -p $(TOPDIR)/config/vimrc tmpdir/config/.vimrc
	$(TOPDIR)/bin/fmod -R *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -f Dockerfile -t $(IMAGE) .
	rm -rf tmpdir

.PHONY: run
run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) --hostname $(NAME) $(IMAGE) $(COMMAND) || exit 0

.PHONY: clean
clean:
	docker rmi -f $(IMAGE) ||:
	docker rmi -f `grep FROM Dockerfile | cut -f2 -d" "` ||:
