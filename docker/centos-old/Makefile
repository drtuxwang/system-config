NAME= centos
VERSION := 6
IMAGE := drtuxwang/$(NAME):$(VERSION)

# Docker build
BASE_IMAGE := drtuxwang/$(NAME)-base:$(VERSION)
SANDBOX_IMAGE := drtuxwang/$(NAME)-sandbox:$(VERSION)
DEPENDENT_IMAGES := sandbox-gcc
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
ifndef DOCKER_RUN_COMMAND
	DOCKER_RUN_COMMAND=
endif


default: build
	docker images

.PHONY: pull
pull:
	docker pull `grep FROM Dockerfile-base | cut -f2 -d" "`

.PHONY: build
build:
	rm -rf tmpdir
	mkdir -p tmpdir/bin tmpdir/root
	cp -p $(TOPDIR)/bin/* tmpdir/bin/
	cp -p $(TOPDIR)/config/bashrc tmpdir/root/.bashrc
	cp -p $(TOPDIR)/config/vimrc tmpdir/root/.vimrc
	$(TOPDIR)/etc/setmod *
	@echo "\n*** Building \"$(BASE_IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) -f Dockerfile-base -t $(BASE_IMAGE) .
	@echo "\n*** Building \"$(SANDBOX_IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) -f Dockerfile-sandbox -t $(SANDBOX_IMAGE) .
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) -f Dockerfile -t $(IMAGE) .
	rm -rf tmpdir
	for IMAGE in $(DEPENDENT_IMAGES); do \
		make -C $$IMAGE build || exit 1; \
	done

.PHONY: run
run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) \
		--hostname `echo $(NAME)-$(VERSION) | sed -e "s/[.]//g"` \
		$(IMAGE) \
		$(DOCKER_RUN_COMMAND) \
		||:

.PHONY: version
version:
	@docker run $(DOCKER_RUN_FLAGS) $(IMAGE) cat /etc/system-release 2> /dev/null | \
		sed -e "s@.*release @`pwd`: @" | awk '{printf("%s CentOS Linux %s\n", $$1, $$2)}'
	@for IMAGE in $(DEPENDENT_IMAGES); do \
		make --no-print-directory -C $$IMAGE version ||:; \
	done

.PHONY: clean
clean:
	for IMAGE in $(DEPENDENT_IMAGES); do \
		make -C $$IMAGE clean; \
	done
	docker rmi -f $(IMAGE) $(SANDBOX_IMAGE) $(BASE_IMAGE) `grep FROM Dockerfile* | cut -f2 -d" "` ||:
