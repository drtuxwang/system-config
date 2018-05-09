NAME := ubuntu
VERSION = 14.04
IMAGE := drtuxwang/$(NAME):$(VERSION)
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-quota=1000000 \
	--cpu-shares=50000 \
	--memory=1000m \
	--memory-reservation=50m \
	--volume=/shared:/shared
TOPDIR := ../..


default: build
	docker images

pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`

build:
	rm -rf tmpdir
	mkdir -p tmpdir/bin tmpdir/config
	cp -p $(TOPDIR)/bin/* tmpdir/bin/
	cp -p $(TOPDIR)/config/bashrc tmpdir/config/.bashrc
	cp -p $(TOPDIR)/config/vimrc tmpdir/config/.vimrc
	$(TOPDIR)/bin/fmod -R *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -t $(IMAGE) .
	rm -rf tmpdir

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) --hostname $(NAME)-old $(IMAGE) ||:

clean:
	docker rmi -f $(IMAGE) ||:
	docker rmi -f `grep FROM Dockerfile | cut -f2 -d" "` ||:
