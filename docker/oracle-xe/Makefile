NAME := oracle-xe
VERSION := latest
IMAGE := drtuxwang/$(NAME):$(VERSION)
TOPDIR := ../..

FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-quota=1000000 \
	--cpu-shares=50000 \
	--memory=2000m \
	--memory-reservation=50m \
	--volume=/shared:/shared

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
		--publish 1521:1521 \
		--hostname `echo $(NAME)-$(VERSION) | sed -e "s/[.]//g"` \
		--workdir /u01/app/oracle/product/11.2.0/xe \
		$(IMAGE) ||:

.PHONY: version
version:
	@docker run -it $(FLAGS) $(IMAGE) bash -i -c dbv 2> /dev/null | grep "^DBVERIFY: Release" | sed -e "s@^DBVERIFY: Release@`pwd`: Oracle XE@;s@ -.*@@"

.PHONY: clean
clean:
	docker rmi -f $(IMAGE) ||:
	docker rmi -f `grep FROM Dockerfile | cut -f2 -d" "` ||:
