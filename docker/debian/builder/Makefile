NAME := debian
VERSION = 8
IMAGE := drtuxwang/$(NAME)-builder:$(VERSION)
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
		--name $(NAME)-builder-dock \
		--hostname $(NAME)-builder-dock \
		$(IMAGE) /etc/docker-init || exit 0

irun:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) $(FLAGS_SHELL) \
		--name $(NAME)-ibuilder-dock \
		--hostname $(NAME)-ibuilder-dock \
		$(IMAGE) || exit 0

