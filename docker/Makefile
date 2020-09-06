IMAGES="drtuxwang/.*"

BUILD_DIRS := \
	alpine-3.10 \
	alpine-stable \
	alpine-stable-i386 \
	amazonlinux-stable \
	busybox-stable \
	centos-7 \
	centos-stable \
	clearlinux-latest \
	debian-9 \
	debian-stable \
	debian-stable-i386 \
	docker-stable \
	golang-stable \
	python-stable \
	registry-stable \
	sudo \
	ubuntu-16.04 \
	ubuntu-18.04 \
	ubuntu-stable

TEST_DIRS := \
	python-3.6

.PHONY: default
default: build status

.PHONY: status
status:
	docker images | grep "^$(IMAGES) " | sort
	docker system df

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

.PHONY: build
build:
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR build || exit 1:; \
	done

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
	docker system prune
	@echo
	docker images
	@echo
	docker volume ls
	@echo
	docker ps
	@echo
	docker system df

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
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR rmi; \
	done
