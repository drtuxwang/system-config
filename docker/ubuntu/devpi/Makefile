NAME := ubuntu
VERSION = latest
IMAGE := drtuxwang/$(NAME)-devpi:$(VERSION)
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

pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`

build:
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -t $(IMAGE) .

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) \
		--publish 8080:8080 \
		--hostname $(NAME)-devpi \
		$(IMAGE) || exit 0

clean:
	docker rmi -f $(IMAGE) ||:
