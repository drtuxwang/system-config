BUILD_DIRS := \
	alpine-3.10 \
	alpine-i386-3.10 \
	amazonlinux-2 \
	busybox-1.30 \
	centos-7 \
	centos-8 \
	clearlinux \
	debian-10 \
	debian-i386-10 \
	docker-19.03 \
	golang-1.13 \
	python-3.6 \
	registry-2 \
	sudo \
	ubuntu-18.04 \
	ubuntu-20.04

TEST_DIRS := \
	python-3.6

# Default Sandbox distro
ifndef DIST
	DIST=debian
endif


.PHONY: default
default: build

.PHONY: project
project:
	python3 -m cookiecutter ../cookiecutter/docker

.PHONY: check-base
check-base:
	grep "^FROM" */Dockerfile* | sort

.PHONY: pull
pull:
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR pull || exit 1; \
	done
	docker images

.PHONY: build
build:
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR build || exit 1:; \
	done
	docker images

.PHONY: test
test:
	for DIR in $(TEST_DIRS); do \
		make -C $$DIR test; \
	done

.PHONY: version
version:
	@for DIR in $(BUILD_DIRS); do \
		make --no-print-directory -C $$DIR version || exit 1; \
	done

.PHONY: run-sandbox
run-sandbox:
	make -C $(DIST)/sandbox run

.PHONY: run-sudo
run-sudo:
	make -C sudo run

.PHONY: push
push:
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR push || exit 1; \
	done

.PHONY: gc
gc:
	docker ps -f status=exited -q | xargs -r docker rm -v
	docker images -f dangling=true -q | xargs -r docker rmi
	docker images
	docker volume ls
	docker ps

.PHONY: load
load:
	for FILE in *.tar; do \
		 docker load -i $$FILE; \
	done

.PHONY: save
save:
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR save; \
	done

.PHONY: rmi
rmi:
	make gc
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR rmi; \
	done
	make gc
