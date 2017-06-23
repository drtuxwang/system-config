default: all

all: build-all
	docker images

clean:
	cd alpine-3.5 && make clean ||:
	cd centos-7 && make clean ||:
	cd debian-7 && make clean ||:
	cd debian-8 && make clean ||:
	cd debian-9 && make clean ||:
	cd jailbreak && make clean ||:
	cd jenkins && make clean ||:
	cd registry-2 && make clean ||:
	cd ubuntu-16.04 && make clean ||:

pull:
	cd alpine-3.5 && make pull
	cd centos-7 && make pull
	cd debian-7 && make pull
	cd debian-8 && make pull
	cd debian-9 && make pull
	cd registry-2 && make pull
	cd ubuntu-16.04 && make pull

build-all:
	cd alpine-3.5 && make build
	cd centos-7 && make build
	cd debian-7 && make build-all
	cd debian-8 && make build-all
	cd debian-9 && make build-all
	cd jailbreak && make build
	cd registry-2 && make build
	cd ubuntu-16.04 && make build
