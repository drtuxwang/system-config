NAME := jenkins
VERSION := lts
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

# PHONY targets
.PHONY: pull build run version clean

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
		--volume=/var/lib/jenkins:/var/lib/jenkins \
		--publish 8080:8080 \
		--hostname $(NAME) \
		--workdir /var/lib/jenkins \
		$(IMAGE) ||:

version:
	@docker run $(FLAGS) --entrypoint bash $(IMAGE) jenkins.sh --version 2> /dev/null | sed -e "s@^@`pwd`: Jenkins @"

clean:
	docker rmi -f $(IMAGE) ||:
	docker rmi -f `grep FROM Dockerfile | cut -f2 -d" "` ||:
