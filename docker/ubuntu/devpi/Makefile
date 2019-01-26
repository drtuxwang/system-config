NAME := ubuntu-devpi
VERSION := 18.04
IMAGE := drtuxwang/$(NAME):$(VERSION)

# Docker build
TOPDIR := ../../..
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


default: build
	docker images

.PHONY: build
build:
	rm -rf tmpdir
	mkdir -p tmpdir/bin tmpdir/config
	cp -p $(TOPDIR)/bin/* tmpdir/bin/
	cp -p $(TOPDIR)/config/bashrc tmpdir/config/.bashrc
	cp -p $(TOPDIR)/config/vimrc tmpdir/config/.vimrc
	$(TOPDIR)/bin/fmod -R *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) -t $(IMAGE) .
	rm -rf tmpdir

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
		   awk '{printf("'`pwd`': devpi-server %s\n", $$1)}'

.PHONY: clean
clean:
	docker rmi -f $(IMAGE) ||:
