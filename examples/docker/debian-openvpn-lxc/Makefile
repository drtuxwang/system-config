IMAGE := debian-openvpn-lxc

default: build

build:
	@echo "\n*** Building Docker image ***"
	docker build -t $(IMAGE) .
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
		--name $(IMAGE) \
		--hostname $(IMAGE) \
		$(IMAGE) /etc/docker-init || exit 0

exec:
	@echo "\n*** Execing in Docker container ***"
	docker exec --interactive --tty $(IMAGE) /etc/docker-exec || exit 0
