BASE_IMAGE := ubuntu:20.04
IMAGE := drtuxwang/ubuntu:stable

TOPDIR := ../..
ifndef DOCKER_BUILD_FLAGS
	DOCKER_BUILD_FLAGS=
endif
BUILD_DIRS := bash dev


.PHONY: default
default: build status

.PHONY: status
status:
	docker images | grep "^$(shell echo $(IMAGE) | sed -e 's/-.*:/:/;s/:/.* /') " | sort

.PHONY: pull
pull:
	docker pull $(BASE_IMAGE)

.PHONY: save
save:
	../docker-save.sh $(BASE_IMAGE)

.PHONY: build
build:
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	rm -rf tmpdir
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR build || exit 1; \
	done

.PHONY: run
run:
	make -C bash run

.PHONY: version
version:
	@for DIR in $(BUILD_DIRS); do \
		make --no-print-directory -C $$DIR version ||:; \
	done

.PHONY: push
push:
	@echo "\n*** Pushing \"$(IMAGE)\" Docker image ***"
	@docker push $(IMAGE)
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR push || exit 1; \
	done

.PHONY: rmi
rmi:
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR rmi; \
	done

.PHONY: rmi-base
rmi-base: rmi
	docker rmi -f $(IMAGE) ||:
