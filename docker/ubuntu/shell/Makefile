NAME := ubuntu
VERSION = 16.04
IMAGE := drtuxwang/$(NAME)-shell:$(VERSION)
IMAGE_X := drtuxwang/$(NAME)-xshell:$(VERSION)
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
	docker rmi -f $(IMAGE) $(IMAGE_X) ||:

build:
	mkdir tmpdir ||: && cp -rp ../../../bin ../../../config tmpdir && tmpdir/bin/fmod -R *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -f Dockerfile-shell -t $(IMAGE) .
	@echo "\n*** Building \"$(IMAGE_X)\" Docker image ***"
	docker build --force-rm=true -f Dockerfile-xshell -t $(IMAGE_X) .
	rm -rf tmpdir

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) $(FLAGS_SHELL) \
		--name $(NAME)-shell-dock \
		--hostname $(NAME)-shell-dock \
		$(IMAGE) || exit 0

xrun:
	@echo "\n*** Running \"$(IMAGE_X)\" Docker container (with graphics) ***"
	docker run $(FLAGS) $(FLAGS_SHELL) \
		--volume=/tmp/.X11-unix:/tmp/.X11-unix \
		--env DISPLAY=$(DISPLAY) \
		--name $(NAME)-xshell-dock \
		--hostname $(NAME)-xshell-dock \
		$(IMAGE_X) || exit 0
