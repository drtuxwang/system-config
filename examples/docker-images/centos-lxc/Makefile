default: build

build:
	@echo "\n*** Building Docker image ***"
	cp -rp ../../../bin ../../../config/bashrc ../../../config/docker-init \
		../../../config/profile ../../../config/vimrc .
	bin/fmod bin/* *
	docker build -t centos-lxc .
	docker images
	rm -rf bin bashrc docker-init profile vimrc

run:
	@echo "\n*** Running Docker container ***"
	docker run --interactive --tty --memory=1024mb \
		--name centos-lxc --hostname centos-lxc --rm centos-lxc

xrun:
	@echo "\n*** Running Docker container ***"
	docker run --interactive --tty --memory=1024mb \
		--env UID=`id -u` --env DISPLAY=$(DISPLAY) --volume /tmp/.X11-unix:/tmp/.X11-unix \
		--name centos-lxc --hostname centos-lxc --rm centos-lxc 
