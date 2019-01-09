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

# Default local port
ifndef LOCALPORT
	LOCALPORT=8080
endif


default: build
	docker images

.PHONY: pull
pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`

.PHONY: build
build:
	rm -rf tmpdir
	mkdir -p tmpdir/config
	cp -p $(TOPDIR)/config/bashrc tmpdir/config/.bashrc
	$(TOPDIR)/bin/fmod -R *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -t $(IMAGE) .
	rm -rf tmpdir

.PHONY: run
run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) \
		--privileged=true \
		--volume=/var/lib/jenkins:/var/lib/jenkins \
		--publish $(LOCALPORT):8080 \
		--hostname `echo $(NAME)-$(VERSION) | sed -e "s/[.]//g"` \
		--workdir /var/lib/jenkins \
		$(IMAGE) ||:

.PHONY: version
version:
	@docker run $(FLAGS) --entrypoint bash $(IMAGE) jenkins.sh --version 2> /dev/null | sed -e "s@^@`pwd`: Jenkins @"

.PHONY: clean
clean:
	docker rmi -f $(IMAGE) ||:
	docker rmi -f `grep FROM Dockerfile | cut -f2 -d" "` ||:
