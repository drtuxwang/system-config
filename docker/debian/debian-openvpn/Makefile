IMAGE := debian-openvpn
CPUSHARE := --cpu-shares=100000 --cpu-quota=1000000
MEMLIMIT :=  -memory-reservation=64m --memory=1024m
PASSWD := $(HOME)/.docker-passwd

default: build

build:
	@echo "\n*** Building Docker image ***"
	cp -rp ../../../bin ../../../config .
	bin/fmod -R *
	docker build -t $(IMAGE) .
	rm -rf bin config
	docker images

$(PASSWD):
	echo "root:x:0:0:root:/root:/bin/bash\n$(USER):x:`id -u`:`id -g`:-:$(HOME):/bin/bash" > \
	$(HOME)/.docker-passwd

run: $(PASSWD)
	@echo "\n*** Running Docker container ***"
	docker run $(CPUSHARE) $(MEMLIMIT) \
		--rm \
		--interactive \
		--tty \
		--volume="$(PASSWD):/etc/passwd:ro" \
		--volume="/etc/group:/etc/group:ro" \
		--volume=/tmp/.X11-unix:/tmp/.X11-unix \
		--volume=/shared:/shared \
		--env USER=$(USER) \
		--env TERM=$(TERM) \
		--env DISPLAY=$(DISPLAY) \
		--name $(IMAGE) \
		--hostname $(IMAGE) \
		$(IMAGE) /etc/docker-init || exit 0
