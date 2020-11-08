BASE_IMAGE := centos:8
IMAGE := drtuxwang/centos:stable

TOPDIR := ../..
ifndef DOCKER_BUILD_FLAGS
	DOCKER_BUILD_FLAGS=
endif
BUILD_DIRS := bash dev

IMAGE_FILE=../docker-image_$(shell echo  $(BASE_IMAGE) | sed -e "s/\//-/g;s/:/_/").tar
IMAGE_TIME=$(shell docker inspect $(BASE_IMAGE) | grep '"Created":' | cut -f4 -d'"')


.PHONY: default
default: build status

.PHONY: status
status:
	docker images | grep "^$(shell echo $(IMAGE) | sed -e 's/-.*:/:/;s/:/.* /') " | sort

.PHONY: pull
pull:
	docker pull $(BASE_IMAGE)
	docker images | grep "^$(shell echo $(BASE_IMAGE) | sed -e 's/:/.* /') "

.PHONY: build
build:
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
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

.PHONY: save
save:
	docker save $(BASE_IMAGE) -o $(IMAGE_FILE) && touch -d $(IMAGE_TIME) $(IMAGE_FILE)

.PHONY: rmi
rmi:
	for DIR in $(BUILD_DIRS); do \
		make --no-print-directory -C $$DIR rmi; \
	done
	docker rmi -f $(IMAGE) ||:
