NAME := sudo
VERSION := latest
IMAGE := drtuxwang/$(NAME):$(VERSION)

# Docker build
ifndef DOCKER_BUILD_FLAGS
	DOCKER_BUILD_FLAGS=
endif

# Docker run
ifndef DOCKER_RUN_FLAGS
	DOCKER_RUN_FLAGS=
endif
DOCKER_RUN_FLAGS := --rm \
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
	$(DOCKER_RUN_FLAGS)
ifndef DOCKER_RUN_COMMAND
	DOCKER_RUN_COMMAND=
endif


default: build
	docker images

.PHONY: build
build:
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) --force-rm=true -t $(IMAGE) .

.PHONY: run
run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) \
		--privileged=true \
		--hostname `uname -n`-$(NAME) \
		$(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: version
version:
	@echo "`pwd`: scratch"

.PHONY: clean
clean:
	docker rmi -f $(IMAGE) ||:
