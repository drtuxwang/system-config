NAME := debian
VERSION := 8
IMAGE_BASE := drtuxwang/$(NAME)-base:$(VERSION)
IMAGE_SANDBOX := drtuxwang/$(NAME)-sandbox:$(VERSION)
IMAGE := drtuxwang/$(NAME):$(VERSION)
DEPENDENT_IMAGES := sandbox-gcc
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
	@echo "\n*** Building \"$(IMAGE_BASE)\" Docker image ***"
	docker build -f Dockerfile-base -t $(IMAGE_BASE) .
	@echo "\n*** Building \"$(IMAGE_SANDBOX)\" Docker image ***"
	docker build -f Dockerfile-sandbox -t $(IMAGE_SANDBOX) .
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -f Dockerfile -t $(IMAGE) .
	rm -rf tmpdir
	for IMAGE in $(DEPENDENT_IMAGES); do \
		make -C $$IMAGE build || exit 1; \
	done

.PHONY: run
run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) \
		--hostname `echo $(NAME)-$(VERSION) | sed -e "s/[.]//g"` \
		$(IMAGE) \
		$(COMMAND) \
		||:

.PHONY: version
version:
	@docker run $(FLAGS) $(IMAGE) cat /etc/debian_version 2> /dev/null | \
		sed -e "s@^@`pwd`: Debian Linux @"
	@for IMAGE in $(DEPENDENT_IMAGES); do \
		make --no-print-directory -C $$IMAGE version ||:; \
	done

.PHONY: clean
clean:
	for IMAGE in $(DEPENDENT_IMAGES); do \
		make -C $$IMAGE clean; \
	done
	docker rmi -f $(IMAGE) $(IMAGE_SANDBOX) $(IMAGE_BASE) `grep FROM Dockerfile* | cut -f2 -d" "` ||:
