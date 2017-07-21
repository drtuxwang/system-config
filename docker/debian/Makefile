NAME := debian
VERSION = 9
IMAGE := drtuxwang/$(NAME):$(VERSION)
IMAGE_BASE := drtuxwang/$(NAME)-base:$(VERSION)
IMAGE_XBASE := drtuxwang/$(NAME)-xbase:$(VERSION)
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
	docker rmi -f $(IMAGE) $(IMAGE_BASE) $(IMAGE_XBASE) ||:
	docker rmi -f `grep FROM Dockerfile | cut -f2 -d" "` ||:
	cd $(NAME)-old && make clean
	cd $(NAME)-test && make clean

pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`
	cd $(NAME)-old && make pull
	cd $(NAME)-test && make pull

build-all: build
	cd $(NAME)-old && make build
	cd $(NAME)-test && make build
	cd builder && make build
	cd docker && make build
	cd nginx && make build
	cd openvpn && make build
	cd shell && make build
	cd wine && make build

build:
	mkdir tmpdir ||: && cp -rp ../../bin ../../config tmpdir && tmpdir/bin/fmod -R *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -t $(IMAGE) .
	@echo "\n*** Building \"$(IMAGE_BASE)\" Docker image ***"
	docker build -f Dockerfile-base -t $(IMAGE_BASE) .
	@echo "\n*** Building \"$(IMAGE_XBASE)\" Docker image ***"
	docker build -f Dockerfile-xbase -t $(IMAGE_XBASE) .
	rm -rf tmpdir

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) \
		--name $(NAME)-dock \
		--hostname $(NAME)-dock \
		$(IMAGE) || exit 0
