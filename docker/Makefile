IMAGES := "drtuxwang/.*"

BUILD_DIRS := \
	alpine-3.12 \
	alpine-3.13 \
	i386-alpine-3.13 \
	amazonlinux-2 \
	busybox-1.33 \
	centos-7 \
	centos-8 \
	clearlinux-latest \
	debian-9-slim \
	debian-10-slim\
	debian-11-slim\
	i386-debian-10-slim \
	i386-debian-11-slim \
	golang-1.16-alpine \
	httpd-2.4-alpine \
	nginx-1.18-alpine \
	oraclelinux-7-slim \
	oraclelinux-8-slim \
	python-3.8-slim-buster \
	registry-2.6 \
	rockylinux-8 \
	sudo \
	ubuntu-16.04 \
	ubuntu-18.04 \
	ubuntu-20.04
STABLE_IMAGES := \
	drtuxwang/debian-bash:11-slim \
	drtuxwang/debian-xfce:11-slim \
	drtuxwang/nginx:1.18-alpine
TEST_DIRS := \
	python-3.8-slim-buster


.PHONY: default
default: build status

.PHONY: status
status:       # Status of Docker images
	docker images | grep "^$(IMAGES) " | sort
	docker system df

.PHONY: new
new:          # Create new Docker project
	python3 -m cookiecutter ../cookiecutter/docker

.PHONY: check-base
check-base:
	grep "^BASE_IMAGE" */Makefile

.PHONY: pull
pull:         # Pull Docker base image
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR pull || exit 1; \
	done

.PHONY: save
save:         # Save Docker base image as tar file
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR save; \
	done

.PHONY: build
build:        # Build Docker images
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR build || exit 1:; \
	done

.PHONY: run-sudo
run-sudo:     # Run sudo docker container
	make -C sudo run

.PHONY: test
test:         # Run tests
	for DIR in $(TEST_DIRS); do \
		make -C $$DIR test; \
	done

.PHONY: version
version:      # Check versions
	@for DIR in $(BUILD_DIRS); do \
		make --no-print-directory -C $$DIR version || exit 1; \
	done

.PHONY:tag
tag:          # Tag stable Docker images
	for IMAGE in $(STABLE_IMAGES); do \
		echo docker tag $$IMAGE $${IMAGE%:*}:stable; \
		docker tag $$IMAGE $${IMAGE%:*}:stable; \
	done

.PHONY: push
push: tag     # Tag and push stable Docker images
	for IMAGE in $(STABLE_IMAGES); do \
		docker push $$IMAGE ; \
		docker push $${IMAGE%:*}:stable ; \
	done

.PHONY: prune
prune:        # Prune Docker images/containers
	docker system df
	df /var/lib/docker
	docker system prune
	@echo
	docker images
	@echo
	docker volume ls
	@echo
	docker ps
	@echo
	docker system df
	df /var/lib/docker
	@echo
	docker network ls

.PHONY: clean
clean:        # Remove temporary build files
	rm -f docker-image_*

.PHONY: rmi
rmi:          # Remove Docker images
	for IMAGE in $(PUSH_IMAGES); do \
		docker rmi -f $${IMAGE%:*}:stable ||:; \
	done
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR rmi; \
	done

.PHONY: rmi-base
rmi-base: rmi # Remove Docker images including base image
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR rmi-base; \
	done

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
