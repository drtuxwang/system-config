BASE_IMAGE := python:3.7.8-slim-buster
IMAGE := drtuxwang/python:stable

TOPDIR := ../..
ifndef DOCKER_BUILD_FLAGS
	DOCKER_BUILD_FLAGS=
endif
BUILD_DIRS := bash devpi


.PHONY: default
default: build status

.PHONY: status
status:
	docker images | grep "^`echo $(IMAGE) | sed -e 's/-.*:/:/;s/:/.* /'` "

.PHONY: pull
pull:
	docker pull $(BASE_IMAGE)
	docker images | grep "^`echo $(BASE_IMAGE) | sed -e 's/:/.* /'` "

.PHONY: build
build:
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build $(DOCKER_BUILD_FLAGS) --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR build || exit 1; \
	done

.PHONY: test
test:
	make -C bash test

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

.PHONY: save
save:
	docker save $(BASE_IMAGE) -o ../$(shell echo "$(BASE_IMAGE)" | sed -e "s#/#-#g").tar

.PHONY: rmi
rmi:
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR rmi; \
	done
	docker rmi -f $(IMAGE) ||:
