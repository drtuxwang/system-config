PULL_IMAGES := \
	alpine \
	busybox \
	centos \
	centos-previous \
	clearlinux \
	debian \
	debian-previous \
	debian-testing \
	etcd \
	jenkins \
	mongo \
	oracle-xe \
	registry \
	ubuntu \
	ubuntu-previous \
	ubuntu-testing
BUILD_IMAGES := $(PULL_IMAGES) jailbreak
CLEAN_IMAGES := $(BUILD_IMAGES)


default: build

project:
	python3 -m cookiecutter ../cookiecutter/docker

pull:
	for IMAGE in $(PULL_IMAGES); do \
		make -C $$IMAGE pull ||:; \
	done
	docker images

build:
	for IMAGE in $(BUILD_IMAGES); do \
		make -C $$IMAGE build ||:; \
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
