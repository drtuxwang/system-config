default: all

all: build-all
	docker images

pull:
	cd alpine-3.4 && make pull
	cd centos-7 && make pull
	cd ubuntu-16.04 && make pull
	cd debian-7 && make pull
	cd debian-8 && make pull
	cd debian-test && make pull

build-all:
	cd alpine-3.4 && make build
	cd centos-7 && make build
	cd jailbreak && make build
	cd ubuntu-16.04 && make build
	cd debian-7 && make build-all
	cd debian-8 && make build-all
	cd debian-test && make build-all
