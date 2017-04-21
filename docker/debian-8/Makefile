IMAGE := drtuxwang/debian:8
IMAGE_BASE := drtuxwang/debian-base:8
IMAGE_SHELL := drtuxwang/debian-shell:8
IMAGE_XBASE := drtuxwang/debian-xbase:8
IMAGE_XSHELL := drtuxwang/debian-xshell:8
HOSTNAME := jessie-dock
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
	--env TERM=$(TERM) \
	--env USER=$(USER) \
	--name $(HOSTNAME) \
	--hostname $(HOSTNAME)


default: build
	docker images

all: build-all
	docker images

clean:
	cd builder && make clean
	cd docker && make clean
	cd nginx && make clean
	cd openvpn && make clean
	cd wine && make clean
	docker rmi -f $(IMAGE) $(IMAGE_BASE) $(IMAGE_SHELL) $(IMAGE_XBASE) $(IMAGE_XSHELL) ||:
	docker rmi -f `grep FROM Dockerfile | cut -f2 -d" "`

pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`

build-all: build
	cd builder && make build
	cd docker && make build
	cd nginx && make build
	cd openvpn && make build
	cd wine && make build

build:
	mkdir tmpdir ||: && cp -rp ../../bin ../../config tmpdir && tmpdir/bin/fmod -R *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -t $(IMAGE) .
	@echo "\n*** Building \"$(IMAGE_BASE)\" Docker image ***"
	docker build -f Dockerfile-base -t $(IMAGE_BASE) .
	@echo "\n*** Building \"$(IMAGE_SHELL)\" Docker image ***"
	docker build -f Dockerfile-shell -t $(IMAGE_SHELL) .
	@echo "\n*** Building \"$(IMAGE_XBASE)\" Docker image ***"
	docker build -f Dockerfile-xbase -t $(IMAGE_XBASE) .
	@echo "\n*** Building \"$(IMAGE_XSHELL)\" Docker image ***"
	docker build --force-rm=true -f Dockerfile-xshell -t $(IMAGE_XSHELL) .
	rm -rf tmpdir

run:
	@echo "\n*** Running \"$(IMAGE_SHELL)\" Docker container ***"
	docker run $(FLAGS) $(IMAGE_SHELL) || exit 0

xrun: $(PASSWD)
	@echo "\n*** Running \"$(IMAGE_XSHELL)\" Docker container (with graphics) ***"
	docker run $(FLAGS) \
		--volume=/tmp/.X11-unix:/tmp/.X11-unix \
		--env DISPLAY=$(DISPLAY) \
		$(IMAGE_XSHELL) || exit 0
