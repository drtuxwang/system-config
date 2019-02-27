BUILD_DIRS := \
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
	sudo \
	ubuntu-old \
	ubuntu \
	ubuntu-i386 \
	ubuntu-test

TEST_DIRS := ubuntu

# Default Sandbox distro
ifndef DIST
	DIST=ubuntu
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

.PHONY: run-firefox
run-firefox:
	make -C $(DIST)/sandbox-firefox run

.PHONY: run-gcc
run-gcc:
	make -C $(DIST)/sandbox-gcc run

.PHONY: run-python
run-python:
	make -C $(DIST)/sandbox-python run

.PHONY: run-sudo
run-sudo:
	make -C sudo run

.PHONY: run-wine
run-wine:
	make -C $(DIST)/sandbox-wine run

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
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR clean; \
	done
	make gc

