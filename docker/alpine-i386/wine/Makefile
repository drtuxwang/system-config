NAME := alpine-wine-i386
VERSION = latest
IMAGE := drtuxwang/$(NAME):$(VERSION)
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-quota=1000000 \
	--cpu-shares=50000 \
	--memory=1000m \
	--memory-reservation=50m \
	--volume=/shared:/shared \
	--volume=/tmp/.X11-unix:/tmp/.X11-unix \
	--env DISPLAY=$(DISPLAY) \
	--env XAUTH="`xauth list $(DISPLAY)`"

TOPDIR := ../../..

ifndef EXTRA_FLAGS
	EXTRA_FLAGS=
endif
ifndef COMMAND
	COMMAND=
endif


default: build
	docker images

pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`

build:
	rm -rf tmpdir
	mkdir -p tmpdir/bin tmpdir/config
	cp -p $(TOPDIR)/config/docker-xinit tmpdir/config/
	$(TOPDIR)/bin/fmod -R *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -t $(IMAGE) .
	rm -rf tmpdir

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) $(EXTRA_FLAGS) --hostname $(NAME) $(IMAGE) $(COMMAND) ||:

clean:
	docker rmi -f $(IMAGE) ||:
	docker rmi -f `grep FROM Dockerfile | cut -f2 -d" "` ||:
