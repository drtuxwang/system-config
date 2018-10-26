NAME := sudo
VERSION := latest
IMAGE := drtuxwang/$(NAME):$(VERSION)

ifndef FLAGS
	FLAGS=
endif
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-quota=1000000 \
	--cpu-shares=50000 \
	--memory=1000m \
	--memory-reservation=50m \
	`ls -1d /* | grep -v "/proc$$" | awk '{printf("--volume=%s:%s ",$$1,$$1)}'` \
	--volume="/etc/hosts:/etc/hosts" \
	--volume="/etc/passwd:/etc/passwd:ro" \
	--volume="/etc/group:/etc/group:ro" \
	$(FLAGS)
ifndef COMMAND
	COMMAND=
endif


default: build
	docker images

build:
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build --force-rm=true -t $(IMAGE) .

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) \
		--privileged=true \
		--hostname `uname -n`-$(NAME) \
		$(IMAGE) $(COMMAND) ||:

version:
	@echo "`pwd`: scratch"

clean:
	docker rmi -f $(IMAGE) ||:
