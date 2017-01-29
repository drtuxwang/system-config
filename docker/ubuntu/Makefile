IMAGE := ubuntu-base
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-period=100000 \
	--cpu-shares=100000 \
	--cpu-quota=1000000 \
	--memory-reservation=64m \
	--memory=1024m \
	--name $(IMAGE)-dock \
	--hostname $(IMAGE)-dock


default: build
	docker images

all: build-all
	docker images

pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`

build-all: build

build:
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	mkdir tmpdir ||:
	cp -rp ../../bin ../../config tmpdir
	tmpdir/bin/fmod -R *
	docker build -t $(IMAGE) .
	rm -rf tmpdir
	rm -rf bin config

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) \
		$(IMAGE) bash || exit 0
