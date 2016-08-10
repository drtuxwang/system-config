default: build

build:
	@echo "\n*** Building Docker image ***"
	cp -rp ../../../bin .
	bin/fmod bin/*
	cp -p ../../../config/bashrc ../../../config/docker-init \
		../../../config/profile ../../../config/vimrc tmpdir
	docker build -t centos-7-lxc .
	docker images
	rm -rf bin bashrc docker-init profile vimrc

run:
	@echo "\n*** Running Docker container ***"
	docker run --interactive --tty --memory=1024mb \
		--name centos-7-lxc --hostname centos-7-lxc --rm centos-7-lxc

xrun:
	@echo "\n*** Running Docker container ***"
	docker run --interactive --tty --memory=1024mb \
		--env UID=`id -u`--env DISPLAY=$(DISPLAY) --volume /tmp/.X11-unix:/tmp/.X11-unix \
		--name centos-7-lxc --hostname centos-7-lxc --rm centos-7-lxc 
