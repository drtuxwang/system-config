NAME := nginx:1.16.1-alpine
IMAGE := drtuxwang/$(NAME)

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
ifndef LOCALPORT
	LOCALPORT=8080
endif


.PHONY: default
default: build
	docker images

.PHONY: pull
pull:
	docker pull $(shell grep FROM Dockerfile | cut -f2 -d" ")

.PHONY: build
build:
	rm -rf tmpdir
	mkdir -p tmpdir/bin tmpdir/root
	cp -p $(TOPDIR)/bin/sysinfo.sh tmpdir/bin/
	cp -p $(TOPDIR)/config/bashrc tmpdir/root/.bashrc
	$(TOPDIR)/etc/setmod *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) -t $(IMAGE) .
	rm -rf tmpdir

.PHONY: run
run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) \
		--publish $(LOCALPORT):80 \
		--hostname $(NAME) \
		--workdir /var/lib/nginx \
		$(IMAGE) \
		||:

.PHONY: version
version:
	@docker run --entrypoint nginx $(IMAGE) -v 2>&1 | grep "^nginx version:" | \
		sed -e "s@nginx/@@" | awk '{printf("'$(shell pwd)': nginx %s\n", $$3)}'

.PHONY: clean
clean:
	docker rmi -f $(IMAGE) ||:
