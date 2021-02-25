IMAGES="drtuxwang/.*"

BUILD_DIRS := \
	alpine-3.11 \
	alpine-3.12 \
	i386-alpine-3.12 \
	amazonlinux-2 \
	busybox-1.31 \
	centos-7 \
	centos-8 \
	clearlinux-latest \
	debian-9-slim \
	debian-10-slim\
	i386-debian-10-slim \
	docker-19.03 \
	golang-1.14-alpine \
	oraclelinux-7-slim \
	oraclelinux-8-slim \
	python-3.7-slim-buster \
	registry-2.6 \
	sudo \
	ubuntu-16.04 \
	ubuntu-18.04 \
	ubuntu-20.04

PUSH_IMAGES := \
	drtuxwang/debian-bash:10-slim \
	drtuxwang/debian-xfce:10-slim

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

.PHONY: push
push:
	for IMAGE in $(PUSH_IMAGES); do \
		docker tag $$IMAGE $${IMAGE%:*}:stable ; \
	done
	for IMAGE in $(PUSH_IMAGES); do \
		docker push $$IMAGE ; \
		docker push $${IMAGE%:*}:stable ; \
	done

.PHONY: version
version:
	@for DIR in $(BUILD_DIRS); do \
		make -C $$DIR version || exit 1; \
	done

.PHONY: run-sudo
run-sudo:
	make -C sudo run

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
	./docker-load.sh *.tar*

.PHONY: save
save:
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR save; \
	done

.PHONY: rmi
rmi:
	for IMAGE in $(PUSH_IMAGES); do \
		docker rmi -f $${IMAGE%:*}:stable ||:; \
	done
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR rmi; \
	done

.PHONY: rmi-base
rmi-base:
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR rmi-base; \
	done

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
