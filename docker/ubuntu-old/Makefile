NAME := ubuntu
VERSION := 16.04
IMAGE := drtuxwang/$(NAME):$(VERSION)
DEPENDENT_IMAGES := sandbox
TOPDIR := ../..

FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-quota=1000000 \
	--cpu-shares=50000 \
	--memory=1000m \
	--memory-reservation=50m \
	--volume=/shared:/shared

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
	$(TOPDIR)/bin/fmod -R *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -f Dockerfile-base -t `grep FROM Dockerfile | cut -f2 -d" "` .
	docker build -f Dockerfile -t $(IMAGE) .
	rm -rf tmpdir
	for IMAGE in $(DEPENDENT_IMAGES); do \
		make -C $$IMAGE build || exit 1; \
	done

.PHONY: run
run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) --hostname $(NAME) $(IMAGE) || exit 0

.PHONY: version
version:
	@docker run $(FLAGS) $(IMAGE) cat /etc/os-release 2> /dev/null | \
		grep "^VERSION=" | sed -e "s@.*=\"@`pwd`: Ubuntu Linux @;s@ (.*@@"

.PHONY: clean
clean:
	for IMAGE in $(DEPENDENT_IMAGES); do \
		make -C $$IMAGE clean; \
	done
	docker rmi -f $(IMAGE) `grep FROM Dockerfile* | cut -f2 -d" "` ||:
