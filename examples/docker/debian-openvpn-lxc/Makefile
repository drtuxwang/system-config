default: build

build:
	@echo "\n*** Building Docker image ***"
	docker build -t debian-openvpn-lxc .
	docker images

run:
	@echo "\n*** Running Docker container ***"
	docker run --memory=1024mb \
		--privileged \
		--rm \
		--interactive \
		--tty \
		--volume /tmp/.X11-unix:/tmp/.X11-unix \
		--volume /shared:/shared \
		--volume /etc/openvpn:/etc/openvpn:ro \
		--volume /etc/ssl/certs:/etc/ssl/certs:ro \
		--env ID="`id`" \
		--env DISPLAY=$(DISPLAY) \
		--name debian-openvpn-lxc \
		--hostname debian-openvpn-lxc \
		debian-openvpn-lxc /etc/docker-init || exit 0

exec:
	@echo "\n*** Execing in Docker container ***"
	docker exec --interactive --tty debian-openvpn-lxc /etc/docker-exec || exit 0
