default: build

build:
	@echo "\n*** Building Docker image ***"
	cp -rp ../../../bin ../../../config .
	bin/fmod bin/* *
	docker build -t ubuntu-lxc .
	rm -rf bin config
	docker images

run:
	@echo "\n*** Running Docker container (with X-windows)***"
	docker run --interactive --tty --memory=1024mb \
		--volume /tmp/.X11-unix:/tmp/.X11-unix \
		--volume /shared:/shared \
		--env ID="`id`" \
		--env DISPLAY=$(DISPLAY) \
		--name ubuntu-lxc \
		--hostname ubuntu-lxc \
		--rm ubuntu-lxc || exit 0

exec:
	@echo "\n*** Execing in Docker container ***"
	docker exec --interactive --tty \
		debian-lxc /etc/docker-exec || exit 0
