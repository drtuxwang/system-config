IMAGE := debian9-builder
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
	--name $(IMAGE)-dock \
	--hostname $(IMAGE)-dock


default: build
	docker images

all: build
	docker images

build:
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -t $(IMAGE) .

$(PASSWD):
	echo "root:x:0:0:root:/root:/bin/bash\n$(USER):x:`id -u`:`id -g`:-:$(HOME):/bin/bash" > \
	$(HOME)/.docker-passwd

run: $(PASSWD)
	@echo "\n*** Running \"$(IMAGE)\" Docker container (offline) ***"
	docker run $(FLAGS) --network none $(IMAGE) /etc/docker-init || exit 0

irun: $(PASSWD)
	@echo "\n*** Running \"$(IMAGE)\" Docker container (with network) ***"
	docker run $(FLAGS) $(IMAGE) || exit 0
