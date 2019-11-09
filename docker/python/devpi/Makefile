NAME := python-devpi
IMAGE := drtuxwang/$(NAME)

# Docker build
ifndef DOCKER_BUILD_FLAGS
	DOCKER_BUILD_FLAGS=
endif

# Docker run
DOCKER_RUN_FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-quota=1000000 \
	--cpu-shares=50000 \
	--memory=1000m \
	--memory-reservation=50m \
	--volume=/shared:/shared
ifndef LOCALPORT
	LOCALPORT=8080
endif


.PHONY: default
default: build
	docker images

.PHONY: build
build:
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) -t $(IMAGE) .

.PHONY: run
run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) \
		--publish $(LOCALPORT):8080 \
		--hostname $(NAME) \
		--workdir /var/lib/devpi \
		$(IMAGE) \
		||:

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
