NAME := etcd
VERSION = latest
IMAGE := drtuxwang/$(NAME):$(VERSION)
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-period=100000 \
	--cpu-shares=100000 \
	--cpu-quota=1000000 \
	--memory-reservation=64m \
	--memory=2048m
TOPDIR := ../..


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
		--env ETCDCTL_API=3 \
		--publish 2379:2379 \
		--publish 2380:2380 \
		--hostname $(NAME) \
		$(IMAGE) \
			etcd \
			--name my_etcd0 \
			--data-dir /var/lib/etcd/data \
			--wal-dir /var/lib/etcd/wal || exit 0

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
			migrate || exit 0

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
			snapshot restore /var/lib/etcd/snapshot.db || exit 0

clean:
	docker rmi -f $(IMAGE) ||:
	docker rmi -f `grep FROM Dockerfile | cut -f2 -d" "` ||:
