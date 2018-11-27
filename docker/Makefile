PULL_IMAGES := \
	alpine \
	alpine-i386 \
	busybox \
	centos-old \
	centos \
	clearlinux \
	debian-old \
	debian \
	debian-test \
	etcd \
	golang \
	jenkins \
	mongodb \
	oracle-xe \
	registry \
	ubuntu-old \
	ubuntu \
	ubuntu-i386 \
	ubuntu-test
BUILD_IMAGES := $(PULL_IMAGES) sudo
CLEAN_IMAGES := $(BUILD_IMAGES)

# Default Sandbox distro
ifndef DIST
	DIST=ubuntu/sandbox
endif

default: build

.PHONY: project
project:
	python3 -m cookiecutter ../cookiecutter/docker

.PHONY: check-base
check-base:
	grep "^FROM" */Dockerfile* | sort

.PHONY: pull
pull:
	for IMAGE in $(PULL_IMAGES); do \
		make -C $$IMAGE pull || exit 1; \
	done
	docker images

.PHONY: build
build:
	for IMAGE in $(BUILD_IMAGES); do \
		make -C $$IMAGE build || exit 1:; \
	done
	docker images

.PHONY: version
version:
	@for IMAGE in $(BUILD_IMAGES); do \
		make --no-print-directory -C $$IMAGE version || exit 1; \
	done

.PHONY: gc
gc:
	docker ps -f status=exited -q | xargs -r docker rm -v
	docker images -f dangling=true -q | xargs -r docker rmi
	docker images
	docker volume ls
	docker ps

.PHONY: clean
clean:
	make gc
	for IMAGE in $(CLEAN_IMAGES); do \
		make -C $$IMAGE clean; \
	done
	make gc

.PHONY: run-sandbox
run-sandbox:
	make -C $(DIST) run

.PHONY: run-sudo
run-sudo:
	make -C sudo run

.PHONY: run-wine
run-wine:
	make -C $(DIST)/wine run
