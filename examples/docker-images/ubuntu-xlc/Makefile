default: build

build:
	@echo "\n*** Building Docker image ***"
	cp -rp ../../../bin ../../../config/bashrc ../../../config/docker-init \
		../../../config/profile ../../../config/vimrc .
	bin/fmod bin/* *
	docker build -t ubuntu-lxc .
	docker images
	rm -rf bin bashrc docker-init profile vimrc

run:
	@echo "\n*** Running Docker container (with X-windows)***"
	docker run --interactive --tty --memory=1024mb \
		--env ID="`id`" --env DISPLAY=$(DISPLAY) --volume /tmp/.X11-unix:/tmp/.X11-unix \
		--name ubuntu-lxc --hostname ubuntu-lxc --rm ubuntu-lxc
