default: all

all: build-all
	docker images

pull:
	cd alpine && make pull
	cd centos && make pull
	cd debian && make pull
	cd ubuntu && make pull

build-all:
	cd alpine && make build-all
	cd centos && make build-all
	cd debian && make build-all
	cd ubuntu && make build-all
