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
	jenkins \
	mongo \
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
	DIST=ubuntu
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

version:
	@for IMAGE in $(BUILD_IMAGES); do \
		make --no-print-directory -C $$IMAGE version || exit 1; \
	done

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

run-sandbox:
	make -C $(DIST)/sandbox run

run-sudo:
	make -C sudo run

run-wine:
	make -C ubuntu/wine run
