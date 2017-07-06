NAME := debian
VERSION = 8
IMAGE := drtuxwang/$(NAME):$(VERSION)
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-period=100000 \
	--cpu-shares=100000 \
	--cpu-quota=1000000 \
	--memory-reservation=64m \
	--memory=1024m


default: build
	docker images

all: build-all
	docker images

clean:
	docker rmi -f $(IMAGE) $(IMAGE_BASE) $(IMAGE_XBASE) ||:
	docker rmi -f `grep FROM Dockerfile | cut -f2 -d" "` ||:
	cd old && make clean
	cd new && make clean

pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`
	cd old && make pull
	cd new && make pull

build-all: build
	cd old && make build
	cd new && make build

build:
	mkdir tmpdir ||: && cp -rp ../../bin ../../config tmpdir && tmpdir/bin/fmod -R *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -t $(IMAGE) .
	rm -rf tmpdir

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) \
		--name $(NAME)-dock \
		--hostname $(NAME)-dock \
		$(IMAGE) || exit 0
