PULL_IMAGES := \
		alpine busybox centos centos-previous clearlinux debian debian-previous \
		debian-testing etcd registry ubuntu ubuntu-previous ubuntu-testing
BUILD_IMAGES := $(PULL_IMAGES) jailbreak
CLEAN_IMAGES := $(BUILD_IMAGES) jenkins oracle-xe


default: build

project:
	python3 -m cookiecutter ../cookiecutter/docker

pull:
	for IMAGE in $(PULL_IMAGES); do \
		make -C $$IMAGE pull || exit 1; \
	done
	docker images

build:
	for IMAGE in $(BUILD_IMAGES); do \
		make -C $$IMAGE build || exit 1; \
	done
	docker images

gc:
	docker ps -f status=exited -q | xargs -r docker rm -v
	docker images -f dangling=true -q | xargs -r docker rmi
	docker volume ls -qf dangling=true | xargs -r docker volume rm
	docker images

clean:
	make gc
	for IMAGE in $(CLEAN_IMAGES); do \
		make -C $$IMAGE clean; \
	done
	make gc
