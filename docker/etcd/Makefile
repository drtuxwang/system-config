NAME := etcd
VERSION := 3.2.20
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
	mkdir -p tmpdir/bin tmpdir/config
	cp -p $(TOPDIR)/bin/sysinfo.sh tmpdir/bin/
	cp -p $(TOPDIR)/config/ash-2bash tmpdir/bin/bash
	cp -p $(TOPDIR)/config/bashrc tmpdir/config/.bashrc
	$(TOPDIR)/etc/setmod *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) -t $(IMAGE) .
	rm -rf tmpdir

.PHONY: run
run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(DOCKER_RUN_FLAGS) \
		--volume="/var/lib/etcd:/var/lib/etcd" \
		--env ETCDCTL_API=2 \
		--publish 2379:2379 \
		--publish 2380:2380 \
		--hostname $(shell echo $(NAME)-$(VERSION) | sed -e "s/[.]//g") \
		--workdir /var/lib/etcd \
		$(IMAGE) \
			etcd \
			--name my_etcd0 \
			--data-dir /var/lib/etcd/data \
			--wal-dir /var/lib/etcd/wal ||:

.PHONY: version
version:
	@docker run $(DOCKER_RUN_FLAGS) $(IMAGE) etcd --version 2> /dev/null | grep "^etcd " | sed -e "s@^.* @$(shell pwd): etcd @"

.PHONY: migrate
migrate:
	@echo "\n*** Running \"$(IMAGE)\" Docker container to migrate v2 key store ***"
	docker run $(DOCKER_RUN_FLAGS) \
		--volume="/var/lib/etcd:/var/lib/etcd" \
		--env ETCDCTL_API=3 \
		--hostname $(NAME) \
		$(IMAGE) \
			etcdctl \
			--data-dir /var/lib/etcd/data \
			--wal-dir /var/lib/etcd/wal \
			migrate ||:

.PHONY: restore
restore:
	@echo "\n*** Running \"$(IMAGE)\" Docker container to restore from snapshot ***"
	docker run $(DOCKER_RUN_FLAGS) \
		--volume="/var/lib/etcd:/var/lib/etcd" \
		--env ETCDCTL_API=3 \
		--hostname $(NAME) \
		$(IMAGE) \
			etcdctl \
			--name my_etcd0 \
			--data-dir /var/lib/etcd/data \
			--wal-dir /var/lib/etcd/wal \
			snapshot restore /var/lib/etcd/snapshot.db ||:

.PHONY: clean
clean:
	docker rmi -f $(IMAGE) ||:
	docker rmi -f $(shell grep FROM Dockerfile | cut -f2 -d" ") ||:
