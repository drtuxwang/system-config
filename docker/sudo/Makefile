NAME := sudo
VERSION = latest
IMAGE := drtuxwang/$(NAME):$(VERSION)
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-quota=1000000 \
	--cpu-shares=50000 \
	--memory=1000m \
	--memory-reservation=50m \
	--volume=/shared:/shared


default: build
	docker images

build:
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build --force-rm=true -t $(IMAGE) .

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) \
		--privileged=true \
		`ls -1d /* | grep -v "/proc$$" | awk '{printf("--volume=%s:%s ",$$1,$$1)}'` \
		--volume="/etc/passwd:/etc/passwd:ro" \
		--volume="/etc/group:/etc/group:ro" \
		--workdir $(PWD) \
		--hostname `uname -n`-$(NAME) \
		$(IMAGE) ||:

clean:
	docker rmi -f $(IMAGE) ||:
