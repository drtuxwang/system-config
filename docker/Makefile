IMAGES := "drtuxwang/.*"

BUILD_DIRS := \
	alpine-3.14 \
	i386-alpine-3.14 \
	alpine-3.13 \
	\
	debian-11 \
	i386-debian-11 \
	debian-10 \
	debian-9 \
	ubuntu-22.04 \
	ubuntu-20.04 \
	ubuntu-18.04 \
	\
	centos-8 \
	centos-7 \
	oraclelinux-8 \
	oraclelinux-7 \
	rockylinux-8 \
	amazonlinux-2 \
	\
	busybox-1.33 \
	clearlinux \
	golang-1.16 \
	httpd-2.4 \
	nginx-1.18 \
	python-3.9 \
	registry-2.6 \
	scratch
STABLE_IMAGES := \
	drtuxwang/debian-bash:11-slim \
	drtuxwang/debian-dev:11-slim \
	drtuxwang/debian-docker:11-slim \
	drtuxwang/debian-xfce:11-slim \
	drtuxwang/nginx:1.18-alpine \
	drtuxwang/python-dev:3.9-slim-bullseye \
	drtuxwang/python-full:3.9-slim-bullseye \
	drtuxwang/scratch
TEST_DIRS := \
	python-3.9


.PHONY: default
default: build status

.PHONY: status
status:       # Status of Docker images
	docker images --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.CreatedSince}}\t{{.Size}}" | grep "^$(IMAGES):" | sort
	docker system df

.PHONY: new
new:          # Create new Docker project
	python3 -m cookiecutter ../cookiecutter/docker

.PHONY: check-base
check-base:
	grep "^BASE_IMAGE" */Makefile

.PHONY: pull-all
pull:         # Pull base Docker images
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR pull || exit 1; \
	done

.PHONY: save
save:         # Save base Docker images as tar files
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR save; \
	done
	xz -9 -e --x86 --lzma2=dict=128MiB --threads=1 --verbose docker-image_*.tar

.PHONY: build
build:        # Build Docker images
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR build || exit 1:; \
	done

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

.PHONY: push
push-stable:  # Tag and push stable Docker images
	for IMAGE in $(STABLE_IMAGES); do \
		echo docker tag $$IMAGE $${IMAGE%:*}:stable; \
		docker tag $$IMAGE $${IMAGE%:*}:stable; \
	done
	for IMAGE in $(STABLE_IMAGES); do \
		docker push $$IMAGE ; \
		docker push $${IMAGE%:*}:stable ; \
	done
	docker images --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.CreatedSince}}\t{{.Size}}" | grep "^drtuxwang/.*:stable " | sort

.PHONY: pull
pull-stable:  # Pull stable Docker images
	for IMAGE in $(STABLE_IMAGES); do \
		docker pull $$IMAGE ; \
		docker pull $${IMAGE%:*}:stable ; \
	done
	docker images --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.CreatedSince}}\t{{.Size}}" | grep "^drtuxwang/.*:stable " | sort

.PHONY: prune
prune:        # Prune Docker images/containers
	docker system df
	df /var/lib/docker
	docker system prune
	@echo
	docker images --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.CreatedSince}}\t{{.Size}}"
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
