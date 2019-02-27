NAME := mongodb
VERSION := 3.4.14
IMAGE := drtuxwang/$(NAME):$(VERSION)

# Docker build
TOPDIR := ../..
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


.PHONY: default
default: build
	docker images

.PHONY: pull
pull:
	docker pull $(shell grep FROM Dockerfile | cut -f2 -d" ")

.PHONY: build
build:
	rm -rf tmpdir
	mkdir -p tmpdir/config
	cp -p $(TOPDIR)/config/bashrc tmpdir/config/.bashrc
	$(TOPDIR)/etc/setmod *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) -t $(IMAGE) .
	rm -rf tmpdir

.PHONY: run
run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) \
		--privileged=true \
		--publish 27017:27017 \
		--hostname $(shell echo $(NAME)-$(VERSION) | sed -e "s/[.]//g") \
		--workdir /data/db \
		$(IMAGE) ||:

.PHONY: version
version:
	@docker run $(DOCKER_RUN_FLAGS) $(IMAGE) mongod --version 2> /dev/null \
		| grep "^db version v" | sed -e "s@^@$(shell pwd): Mongo @;s@version v@@"

.PHONY: clean
clean:
	docker rmi -f $(IMAGE) ||:
	docker rmi -f $(shell grep FROM Dockerfile | cut -f2 -d" ") ||:
