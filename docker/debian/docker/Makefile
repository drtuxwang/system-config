NAME := debian
VERSION = 9
IMAGE := drtuxwang/$(NAME)-docker:$(VERSION)
FLAGS := --rm \
	--privileged=true \
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
	--volume /var/run/docker.sock:/var/run/docker.sock \
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
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) $(FLAGS_SHELL) \
		--name $(NAME)-docker-dock \
		--hostname $(NAME)-docker-dock \
		$(IMAGE) || exit 0

