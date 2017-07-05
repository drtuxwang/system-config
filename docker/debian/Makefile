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
	cd builder && make clean
	cd docker && make clean
	cd nginx && make clean
	cd openvpn && make clean
	cd wine && make clean
	cd shell && make clean
	docker rmi -f $(IMAGE) ||:
	docker rmi -f `grep FROM Dockerfile | cut -f2 -d" "` ||:
	cd old && make clean
	cd new && make clean

pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`
	cd old && make pull
	cd new && make pull

build-all: build
	cd shell && make build
	cd builder && make build
	cd docker && make build
	cd nginx && make build
	cd openvpn && make build
	cd wine && make build
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
