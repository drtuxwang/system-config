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

build:
	make -C .. build ||:

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker containers cluster***"
	bash -c "trap 'docker-compose down' EXIT; docker-compose up"

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

migrate:
	@echo "\n*** Running \"$(IMAGE)\" Docker containers to migrate v2 key store ***"
	docker-compose -f docker-compose-migrate.yml up
	docker-compose -f docker-compose-migrate.yml down

restore:
	@echo "\n*** Running \"$(IMAGE)\" Docker containers to restore from snapshot ***"
	docker-compose -f docker-compose-restore.yml up
	docker-compose -f docker-compose-restore.yml down

clean:
	docker volume rm cluster_etcda cluster_etcdb
