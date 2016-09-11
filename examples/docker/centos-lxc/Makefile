default: build

build:
	@echo "\n*** Building Docker image ***"
	cp -rp ../../../bin ../../../config .
	bin/fmod bin/* *
	docker build -t centos-lxc .
	rm -rf bin config
	docker images

run:
	@echo "\n*** Running Docker container (with X-windows)***"
	docker run --memory=1024mb \
		-rm \
		--interactive \
		--tty \
		--volume /tmp/.X11-unix:/tmp/.X11-unix \
		--volume /shared:/shared \
		--env ID="`id`" \
		--env DISPLAY=$(DISPLAY) \
		--name centos-lxc \
		--hostname centos-lxc \
		centos-lxc /etc/docker-init || exit 0

exec:
	@echo "\n*** Execing in Docker container ***"
	docker exec --interactive --tty centos-lxc /etc/docker-exec || exit 0
