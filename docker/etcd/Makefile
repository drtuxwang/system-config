NAME := etcd
VERSION := 3.2.20
IMAGE := drtuxwang/$(NAME):$(VERSION)
TOPDIR := ../..

FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-quota=1000000 \
	--cpu-shares=50000 \
	--memory=1000m \
	--memory-reservation=50m \
	--volume=/shared:/shared


default: build
	docker images

pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`

build:
	rm -rf tmpdir
	mkdir -p tmpdir/bin tmpdir/config
	cp -p $(TOPDIR)/bin/sysinfo.sh tmpdir/bin/
	cp -p $(TOPDIR)/config/ash-2bash tmpdir/bin/bash
	cp -p $(TOPDIR)/config/bashrc tmpdir/config/.bashrc
	$(TOPDIR)/bin/fmod -R *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -t $(IMAGE) .
	rm -rf tmpdir

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) \
		--volume="/var/lib/etcd:/var/lib/etcd" \
		--env ETCDCTL_API=2 \
		--publish 2379:2379 \
		--publish 2380:2380 \
		--hostname $(NAME) \
		--workdir /var/lib/etcd \
		$(IMAGE) \
			etcd \
			--name my_etcd0 \
			--data-dir /var/lib/etcd/data \
			--wal-dir /var/lib/etcd/wal ||:

version:
	@docker run $(FLAGS) $(IMAGE) etcd --version 2> /dev/null | grep "^etcd " | sed -e "s@^.* @`pwd`: etcd @"

migrate:
	@echo "\n*** Running \"$(IMAGE)\" Docker container to migrate v2 key store ***"
	docker run $(FLAGS) \
		--volume="/var/lib/etcd:/var/lib/etcd" \
		--env ETCDCTL_API=3 \
		--hostname $(NAME) \
		$(IMAGE) \
			etcdctl \
			--data-dir /var/lib/etcd/data \
			--wal-dir /var/lib/etcd/wal \
			migrate ||:

restore:
	@echo "\n*** Running \"$(IMAGE)\" Docker container to restore from snapshot ***"
	docker run $(FLAGS) \
		--volume="/var/lib/etcd:/var/lib/etcd" \
		--env ETCDCTL_API=3 \
		--hostname $(NAME) \
		$(IMAGE) \
			etcdctl \
			--name my_etcd0 \
			--data-dir /var/lib/etcd/data \
			--wal-dir /var/lib/etcd/wal \
			snapshot restore /var/lib/etcd/snapshot.db ||:

clean:
	docker rmi -f $(IMAGE) ||:
	docker rmi -f `grep FROM Dockerfile | cut -f2 -d" "` ||:
