PULL_IMAGES := \
	alpine-3.7 \
	alpine-3.7-i386 \
	busybox-1.28 \
	centos-6 \
	centos-7 \
	clearlinux \
	debian-8 \
	debian-9 \
	debian-testing \
	etcd-3.2.20 \
	jenkins-lts \
	mongo-3.4.14 \
	oracle-xe \
	registry-2.6 \
	ubuntu-16.04 \
	ubuntu-18.04 \
	ubuntu-18.04-i386
BUILD_IMAGES := $(PULL_IMAGES) sudo
CLEAN_IMAGES := $(BUILD_IMAGES)

ifndef FLAGS
	FLAGS=
endif
ifndef COMMAND
	COMMAND=
endif


default: build

project:
	python3 -m cookiecutter ../cookiecutter/docker

check-base:
	grep "^FROM" */Dockerfile* | sort

pull:
	for IMAGE in $(PULL_IMAGES); do \
		make -C $$IMAGE pull || exit 1; \
	done
	docker images

build:
	for IMAGE in $(BUILD_IMAGES); do \
		make -C $$IMAGE build || exit 1:; \
	done
	docker images

gc:
	docker ps -f status=exited -q | xargs -r docker rm -v
	docker images -f dangling=true -q | xargs -r docker rmi
	docker images
	docker volume ls
	docker ps

clean:
	make gc
	for IMAGE in $(CLEAN_IMAGES); do \
		make -C $$IMAGE clean; \
	done
	make gc

run-sudo:
	FLAGS="$(FLAGS)" COMMAND="$(COMMAND)" make --quiet -C sudo run

run-wine:
	FLAGS="$(FLAGS)" COMMAND="$(COMMAND)" make --quiet -C ubuntu-18.04-i386/wine run
