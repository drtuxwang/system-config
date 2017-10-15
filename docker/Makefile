default: all

all: build-all
	docker images

clean:
	cd alpine && make clean ||:
	cd centos && make clean ||:
	cd debian && make clean ||:
	cd jailbreak && make clean ||:
	cd jenkins && make clean ||:
	cd oracle-xe && make clean ||:
	cd registry && make clean ||:
	cd ubuntu && make clean ||:

pull:
	cd alpine && make pull
	cd centos && make pull
	cd debian && make pull
	cd registry && make pull
	cd ubuntu && make pull

build-all:
	cd alpine && make build
	cd centos && make build-all
	cd debian && make build-all
	cd jailbreak && make build
	cd registry && make build
	cd ubuntu && make build-all

project:
	python3 -m cookiecutter ../cookiecutter/docker
