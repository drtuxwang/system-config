default: build

build:
	@echo "\n*** Building Docker image ***"
	cp -rp ../../../bin ../../../config/bashrc ../../../config/docker-init \
		../../../config/profile ../../../config/terminalrc ../../../config/vimrc .
	bin/fmod bin/* *
	docker build -t centos-lxc .
	docker images
	rm -rf bin bashrc docker-init profile terminalrc vimrc

run:
	@echo "\n*** Running Docker container (with X-windows)***"
	docker run --interactive --tty --memory=1024mb \
		--volume /tmp/.X11-unix:/tmp/.X11-unix \
		--volume /shared:/shared \
		--env ID="`id`" \
		--env DISPLAY=$(DISPLAY) \
		--name centos-lxc --hostname centos-lxc --rm centos-lxc || exit 0
