BASE_IMAGE := drtuxwang/python:3.6
IMAGE := drtuxwang/python-dev:3.6
NAME := python-dev-36
HOSTNAME := python-36

ifndef DOCKER_BUILD_FLAGS
	DOCKER_BUILD_FLAGS=
endif

ifndef LOCALPORT
	LOCALPORT=8080
endif
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
	--workdir /var/lib/devpi \
	--publish $(LOCALPORT):8080 \
	--name $(NAME) \
	--hostname $(HOSTNAME) \
	$(DOCKER_RUN_FLAGS)
ifndef DOCKER_RUN_COMMAND
	DOCKER_RUN_COMMAND=
endif


.PHONY: default
default: build
	docker images

.PHONY: build
build:
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .

.PHONY: run
run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) $(IMAGE) $(DOCKER_RUN_COMMAND) ||:

.PHONY: version
version:
	@docker run --entrypoint devpi-server $(IMAGE) --version | \
		   awk '{printf("'$(shell pwd)': devpi-server %s\n", $$1)}'

.PHONY: push
push:
	@echo "\n*** Pushing \"$(IMAGE)\" Docker image ***"
	@docker push $(IMAGE)

.PHONY: clean
clean:
	docker rmi -f $(IMAGE) ||:
