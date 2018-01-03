NAME := ubuntu
VERSION = latest
IMAGE := drtuxwang/$(NAME)-wine:$(VERSION)
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
	--volume=/tmp/.X11-unix:/tmp/.X11-unix \
	--env DISPLAY=$(DISPLAY) \
	--env TERM=$(TERM) \
	--env USER=$(USER)


default: build
	docker images

clean:
	docker rmi -f $(IMAGE) ||:

build:
	mkdir tmpdir ||: && cp -rp ../../../bin ../../../config tmpdir && tmpdir/bin/fmod -R *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -t $(IMAGE) .
	rm -rf tmpdir

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container (offline) ***"
	docker run $(FLAGS) $(FLAGS_SHELL) \
		--network none \
		--hostname $(NAME)-wine \
		$(IMAGE) /etc/docker-init || exit 0

irun:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) $(FLAGS_SHELL) \
		--hostname $(NAME)-iwine \
		$(IMAGE) || exit 0

