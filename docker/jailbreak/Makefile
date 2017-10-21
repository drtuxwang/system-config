NAME := jailbreak
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

build:
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build --force-rm=true -t $(IMAGE) .

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) \
		`ls -1d /* | grep -v "/proc$$" | awk '{printf("--volume=%s:%s ",$$1,$$1)}'` \
		--volume="/etc/passwd:/etc/passwd:ro" \
		--volume="/etc/group:/etc/group:ro" \
		--workdir $(PWD) \
		--hostname `uname -n`-$(NAME) \
		$(IMAGE) bash || exit 0
