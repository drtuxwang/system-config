IMAGE := centos-lxc

default: build

build:
	@echo "\n*** Building Docker image ***"
	cp -rp ../../../bin ../../../config .
	bin/fmod bin/* *
	docker build --pull -t $(IMAGE) .
	rm -rf bin config
	docker images

run:
	@echo "\n*** Running Docker container ***"
	docker run --memory=1024mb \
		--rm \
		--interactive \
		--tty \
		--volume /tmp/.X11-unix:/tmp/.X11-unix \
		--volume /shared:/shared \
		--env ID="`id`" \
		--env TERM=$(TERM) \
		--env DISPLAY=$(DISPLAY) \
		--name $(IMAGE) \
		--hostname $(IMAGE) \
		$(IMAGE) /etc/docker-init || exit 0
