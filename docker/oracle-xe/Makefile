NAME := oracle-xe
VERSION := 11.2
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
	--memory=2000m \
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
		--publish 8080:8080 \
		--publish 1521:1521 \
		--hostname $(shell echo $(NAME)-$(VERSION) | sed -e "s/[.]//g") \
		$(IMAGE) ||:

.PHONY: run
connect:
	sqlplus64 system/oracle@localhost

.PHONY: version
version:
	@docker run -it $(DOCKER_RUN_FLAGS) $(IMAGE) dbv 2> /dev/null | grep "^DBVERIFY: Release" | sed -e "s@^DBVERIFY: Release@$(shell pwd): Oracle XE@;s@ -.*@@"

.PHONY: clean
clean:
	docker rmi -f $(IMAGE) ||:
	docker rmi -f $(shell grep FROM Dockerfile | cut -f2 -d" ") ||:
