NAME := debian-docker
VERSION = latest
IMAGE := drtuxwang/$(NAME):$(VERSION)
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
	--volume /var/run/docker.sock:/var/run/docker.sock \
	--env TERM=$(TERM) \
	--env USER=$(USER)


default: build
	docker images

build:
	rm -rf tmpdir
	mkdir -p tmpdir/bin tmpdir/config
	cp -p ../../../bin/* tmpdir/bin/
	cp -p ../../../config/bashrc tmpdir/config/.bashrc
	cp -p ../../../config/vimrc tmpdir/config/.vimrc
	../../../bin/fmod -R *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -t $(IMAGE) .
	rm -rf tmpdir

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) $(FLAGS_SHELL) \
		--privileged=true \
		--hostname $(NAME) \
		$(IMAGE) || exit 0

clean:
	docker rmi -f $(IMAGE) ||:
