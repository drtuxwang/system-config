NAME := ubuntu-nginx
VERSION := 18.04
IMAGE := drtuxwang/$(NAME):$(VERSION)

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


default: build
	docker images

.PHONY: build
build:
	rm -rf tmpdir
	mkdir -p tmpdir/bin tmpdir/config
	cp -p ../../../bin/* tmpdir/bin/
	cp -p ../../../config/bashrc tmpdir/config/.bashrc
	cp -p ../../../config/vimrc tmpdir/config/.vimrc
	../../../etc/setmod *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) -t $(IMAGE) .
	rm -rf tmpdir

.PHONY: run
run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) \
		--publish $(LOCALPORT):80 \
		--hostname `echo $(NAME) | sed -e "s/-/-$(VERSION)-/;s/[.]//g"` \
		--workdir /var/lib/nginx \
		$(IMAGE) \
		||:

.PHONY: version
version:
	@docker run --entrypoint nginx $(IMAGE) -v 2>&1 | grep "^nginx version:" | \
		sed -e "s@nginx/@@" | awk '{printf("'`pwd`': nginx %s\n", $$3)}'

.PHONY: clean
clean:
	docker rmi -f $(IMAGE) ||:
