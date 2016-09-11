default: build

build:
	@echo "\n*** Building Docker image ***"
	docker build -t debian-openvpn-lxc .
	docker images

run:
	@echo "\n*** Running Docker container ***"
	docker run --interactive --tty --memory=1024mb \
		--volume /tmp/.X11-unix:/tmp/.X11-unix \
		--volume /shared:/shared \
		--volume /etc/openvpn:/etc/openvpn:ro \
		--volume /etc/ssl/certs:/etc/ssl/certs:ro \
		--env ID="`id`" \
		--env DISPLAY=$(DISPLAY) \
		--privileged \
		--name debian-openvpn-lxc \
		--hostname debian-openvpn-lxc \
		--rm debian-openvpn-lxc || exit 0
