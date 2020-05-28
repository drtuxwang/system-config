BASE_IMAGE := i386/debian:10-slim
NAME := debian-i386
IMAGE := drtuxwang/$(NAME)

TOPDIR := ../..
ifndef DOCKER_BUILD_FLAGS
	DOCKER_BUILD_FLAGS=
endif
BUILD_DIRS := bash dev


.PHONY: default
default: build
	docker images

.PHONY: pull
pull:
	docker pull $(BASE_IMAGE)

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
	docker save $(BASE_IMAGE) -o ../$(shell echo "$(BASE_IMAGE)" | sed -e "s#/#-#g").tar

.PHONY: clean
clean:
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR clean; \
	done
	docker rmi -f $(IMAGE) $(BASE_IMAGE) ||:
