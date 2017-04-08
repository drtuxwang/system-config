IMAGE := drtuxwang/debian:7
IMAGE_BASE := drtuxwang/debian-base:7
IMAGE_SHELL := drtuxwang/debian-shell:7
HOSTNAME := wheezy-dock
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
	docker rmi -f $(IMAGE) $(IMAGE_BASE) $(IMAGE_SHELL) ||:
	cd builder && make clean

pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`

build-all: build
	cd builder && make build

build:
	mkdir tmpdir ||: && cp -rp ../../bin ../../config tmpdir && tmpdir/bin/fmod -R *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -t $(IMAGE) .
	@echo "\n*** Building \"$(IMAGE_BASE)\" Docker image ***"
	docker build -f Dockerfile-base -t $(IMAGE_BASE) .
	@echo "\n*** Building \"$(IMAGE_SHELL)\" Docker image ***"
	docker build -f Dockerfile-shell -t $(IMAGE_SHELL) .
	rm -rf tmpdir

run:
	@echo "\n*** Running \"$(IMAGE_SHELL)\" Docker container ***"
	docker run $(FLAGS) $(IMAGE_SHELL) || exit 0
