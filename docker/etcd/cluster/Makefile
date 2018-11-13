NAME := etcd
VERSION := latest
IMAGE := drtuxwang/$(NAME):$(VERSION)

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

.PHONY: build
build:
	make -C .. build ||:

.PHONY: run
run:
	@echo "\n*** Running \"$(IMAGE)\" Docker containers cluster***"
	bash -c "trap 'docker-compose down' EXIT; docker-compose up"

.PHONY: volume
volume:
	@echo "\n*** Running \"$(IMAGE)\" Docker container to access volumes ***"
	docker volume create --name cluster_etcda
	docker volume create --name cluster_etcdb
	docker run $(FLAGS) \
		--volume="cluster_etcda:/var/lib/etcd/cluster_etcda" \
		--volume="cluster_etcdb:/var/lib/etcd/cluster_etcdb" \
		--env ETCDCTL_API=2 \
		--hostname $(NAME)-mount \
		--workdir /var/lib/etcd \
		$(IMAGE) bash ||:

.PHONY: migrate
migrate:
	@echo "\n*** Running \"$(IMAGE)\" Docker containers to migrate v2 key store ***"
	docker-compose -f docker-compose-migrate.yml up
	docker-compose -f docker-compose-migrate.yml down

.PHONY: restore
restore:
	@echo "\n*** Running \"$(IMAGE)\" Docker containers to restore from snapshot ***"
	docker-compose -f docker-compose-restore.yml up
	docker-compose -f docker-compose-restore.yml down

.PHONY: clean
clean:
	docker volume rm cluster_etcda cluster_etcdb
