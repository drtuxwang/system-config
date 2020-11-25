BASE_IMAGE := clearlinux:latest
IMAGE := drtuxwang/clearlinux:latest

TOPDIR := ../..
ifndef DOCKER_BUILD_FLAGS
	DOCKER_BUILD_FLAGS=
endif
BUILD_DIRS := bash dev

IMAGE_FILE=../$(shell echo  $(BASE_IMAGE) | sed -e "s/\//-/g;s/:/_/")_image.tar
IMAGE_TIME=$(shell docker inspect $(BASE_IMAGE) | grep '"Created":' | cut -f4 -d'"')


.PHONY: default
default: build status

.PHONY: pull
pull:
	docker pull $(BASE_IMAGE)
	docker images | grep "^$(shell echo $(BASE_IMAGE) | sed -e 's/:/.* /') "

.PHONY: save
save:
	docker save $(BASE_IMAGE) -o $(IMAGE_FILE) && touch -d $(IMAGE_TIME) $(IMAGE_FILE)

.PHONY: build
build:
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR build || exit 1; \
	done

.PHONY: status
status:
	docker images | grep "^$(shell echo $(IMAGE) | sed -e 's/-.*:/:/;s/:/.* /') " | sort

.PHONY: run
run:
	make -C bash run

.PHONY: version
version:
	@for DIR in $(BUILD_DIRS); do \
		make --no-print-directory -C $$DIR version || exit 1; \
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
	docker rmi -f $(IMAGE) ||:
