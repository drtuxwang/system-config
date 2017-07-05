NAME := debian
VERSION = 8
IMAGE_BASE := drtuxwang/$(NAME)-base:$(VERSION)
IMAGE_SHELL := drtuxwang/$(NAME)-shell:$(VERSION)
IMAGE_XBASE := drtuxwang/$(NAME)-xbase:$(VERSION)
IMAGE_XSHELL := drtuxwang/$(NAME)-xshell:$(VERSION)
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-period=100000 \
	--cpu-shares=100000 \
	--cpu-quota=1000000 \
	--memory-reservation=64m \
	--memory=1024m
FLAGS_SHELL := \
	--volume=/etc/passwd:/etc/passwd:ro \
	--volume=/etc/group:/etc/group:ro \
	--volume=/shared:/shared \
	--env TERM=$(TERM) \
	--env USER=$(USER)


default: build
	docker images

clean:
	docker rmi -f $(IMAGE_BASE) $(IMAGE_SHELL) $(IMAGE_XBASE) $(IMAGE_XSHELL) ||:

build:
	mkdir tmpdir ||: && cp -rp ../../../bin ../../../config tmpdir && tmpdir/bin/fmod -R *
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
	docker run $(FLAGS) $(FLAGS_SHELL) \
		--name $(NAME)-shell-dock \
		--hostname $(NAME)-shell-dock \
		$(IMAGE_SHELL) || exit 0

xrun:
	@echo "\n*** Running \"$(IMAGE_XSHELL)\" Docker container (with graphics) ***"
	docker run $(FLAGS) $(FLAGS_SHELL) \
		--volume=/tmp/.X11-unix:/tmp/.X11-unix \
		--env DISPLAY=$(DISPLAY) \
		--name $(NAME)-xshell-dock \
		--hostname $(NAME)-xshell-dock \
		$(IMAGE_XSHELL) || exit 0
