IMAGE := drtuxwang/debian-wine
HOSTNAME := jessie-wine-dock
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-period=100000 \
	--cpu-shares=100000 \
	--cpu-quota=1000000 \
	--memory-reservation=64m \
	--memory=1024m \
	--volume=/etc/passwd:/etc/passwd:ro \
	--volume=/etc/group:/etc/group:ro \
	--volume=/shared:/shared \
	--volume=/tmp/.X11-unix:/tmp/.X11-unix \
	--env DISPLAY=$(DISPLAY) \
	--env TERM=$(TERM) \
	--env USER=$(USER) \
	--name $(HOSTNAME) \
	--hostname $(HOSTNAME)


default: build
	docker images

all: build
	docker images

build:
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -t $(IMAGE) .

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container (offline) ***"
	docker run $(FLAGS) --network none $(IMAGE) /etc/docker-init || exit 0

irun:
	@echo "\n*** Running \"$(IMAGE)\" Docker container (with network) ***"
	docker run $(FLAGS) $(IMAGE) || exit 0
