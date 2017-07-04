IMAGE := drtuxwang/ubuntu:16.04
IMAGE_BASE := drtuxwang/ubuntu-base:16.04
IMAGE_SHELL := drtuxwang/ubuntu-shell:16.04
IMAGE_XBASE := drtuxwang/ubuntu-xbase:16.04
IMAGE_XSHELL := drtuxwang/ubuntu-xshell:16.04
HOSTNAME := ubuntu-dock
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-period=100000 \
	--cpu-shares=100000 \
	--cpu-quota=1000000 \
	--memory-reservation=64m \
	--memory=1024m \
	--name $(HOSTNAME) \
	--hostname $(HOSTNAME)


default: build
	docker images

all: build-all
	docker images

clean:
	docker rmi -f $(IMAGE) $(IMAGE_BASE) $(IMAGE_SHELL) $(IMAGE_XBASE) $(IMAGE_XSHELL) ||:
	docker rmi -f `grep FROM Dockerfile | cut -f2 -d" "`
	cd old && make clean
	cd test && make clean

pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`
	cd old && make pull
	cd test && make pull

build-all: build
	cd old && make build
	cd test && make build

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
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) $(IMAGE) || exit 0

shell:
	@echo "\n*** Running \"$(IMAGE_SHELL)\" Docker container ***"
	docker run $(FLAGS) $(FLAGS_SHELL) $(IMAGE_SHELL) || exit 0

xshell:
	@echo "\n*** Running \"$(IMAGE_XSHELL)\" Docker container (with graphics) ***"
	docker run $(FLAGS) $(FLAGS_SHELL) \
		--volume=/tmp/.X11-unix:/tmp/.X11-unix \
		--env DISPLAY=$(DISPLAY) \
		$(IMAGE_XSHELL) || exit 0
