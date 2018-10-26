NAME := mongo
VERSION := 3.4.14
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
	mkdir -p tmpdir/config
	cp -p $(TOPDIR)/config/bashrc tmpdir/config/.bashrc
	$(TOPDIR)/bin/fmod -R *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -t $(IMAGE) .
	rm -rf tmpdir

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) \
		--privileged=true \
		--publish 27017:27017 \
		--hostname $(NAME) \
		--workdir /data/db \
		$(IMAGE) ||:

version:
	@docker run $(FLAGS) $(IMAGE) mongod --version 2> /dev/null \
		| grep "^db version v" | sed -e "s@^@`pwd`: Mongo @;s@version v@@"

clean:
	docker rmi -f $(IMAGE) ||:
	docker rmi -f `grep FROM Dockerfile | cut -f2 -d" "` ||:
