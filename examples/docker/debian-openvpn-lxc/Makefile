IMAGE := debian-openvpn-lxc

default: build

build:
	@echo "\n*** Building Docker image ***"
	cp -rp ../../../config .
	docker build -t $(IMAGE) .
	rm -rf config
	docker images

run:
	@echo "\n*** Running Docker container ***"
	docker run --memory=1024mb \
		--privileged \
		--rm \
		--interactive \
		--tty \
		--volume="/etc/passwd:/etc/passwd:ro" \
		--volume="/etc/group:/etc/group:ro" \
		--volume=/tmp/.X11-unix:/tmp/.X11-unix \
		--volume=/shared:/shared \
		--env USER=$(USER) \
		--env TERM=$(TERM) \
		--env DISPLAY=$(DISPLAY) \
		--name $(IMAGE) \
		--hostname $(IMAGE) \
		$(IMAGE) /etc/docker-init || exit 0
