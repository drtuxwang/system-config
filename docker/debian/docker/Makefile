IMAGE := debian8-docker
PASSWD := $(HOME)/.docker-passwd
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-period=100000 \
	--cpu-shares=100000 \
	--cpu-quota=1000000 \
	--memory-reservation=64m \
	--memory=1024m \
	--volume=/etc/group:/etc/group:ro \
	--volume=$(PASSWD):/etc/passwd:ro \
	--volume=/shared:/shared \
	--volume=/tmp/.X11-unix:/tmp/.X11-unix \
	--env DISPLAY=$(DISPLAY) \
	--env TERM=$(TERM) \
	--env USER=$(USER) \
	--privileged=true \
	--volume /var/run/docker.sock:/var/run/docker.sock \
	--name $(IMAGE)-dock \
	--hostname $(IMAGE)-dock


default: build
	docker images

all: build
	docker images

build:
	mkdir tmpdir ||: && cp -rp ../../../bin ../../../config tmpdir && tmpdir/bin/fmod -R *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -t $(IMAGE) .
	rm -rf tmpdir

$(PASSWD):
	echo "root:x:0:0:root:/root:/bin/bash\n$(USER):x:`id -u`:`id -g`:-:$(HOME):/bin/bash" > \
	$(HOME)/.docker-passwd

run: $(PASSWD)
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) $(IMAGE) || exit 0
