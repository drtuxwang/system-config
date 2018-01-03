NAME := registry
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


default: build
	docker images

clean:
	docker rmi -f $(IMAGE) ||:
	docker rmi -f `grep FROM Dockerfile | cut -f2 -d" "` ||:

pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`

build:
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -t $(IMAGE) .

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) \
		--volume=/var/lib/registry:/var/lib/registry \
		--publish 5000:5000 \
		--hostname $(NAME) \
		$(IMAGE) || exit 0
