IMAGES := "drtuxwang/.*"

BUILD_DIRS := \
	alpine-3.18 \
	i386-alpine-3.18 \
	alpine-3.17 \
	\
	debian-12 \
	i386-debian-12 \
	debian-11 \
	i386-debian-11 \
	debian-10 \
	ubuntu-24.04 \
	ubuntu-22.04 \
	ubuntu-20.04 \
	\
	almalinux-9 \
	almalinux-8 \
	oraclelinux-9 \
	oraclelinux-8 \
	rockylinux-9 \
	rockylinux-8 \
	centos-7 \
	\
	busybox-1.36 \
	golang-1.22 \
	httpd-2.4 \
	nginx-1.26 \
	python-3.12 \
	registry-2.6 \
	scratch
STABLE_DIRS := \
	debian-12/ops \
	debian-12/xfce \
	nginx-1.26 \
	python-3.12/pip \
	scratch
TEST_DIRS := \
	python-3.12


.PHONY: default
default: build status # Default

.PHONY: status
status:               # Status of Docker images
	../bin/docker-images
	docker system df

.PHONY: new
new:                  # Create new Docker project
	python3 -m cookiecutter ../cookiecutter/docker

.PHONY: check-base
check-base:           # Show base Docker images
	grep "^BASE_IMAGE" */Makefile

.PHONY: pull
pull:                 # Pull Docker base images
	for DIR in $(BUILD_DIRS); do \
		make --no-print-directory --directory $$DIR pull || exit 1; \
	done

.PHONY: pull-save
pull-save:            # Pull updated Docker images and save to tar archives
	for DIR in $(BUILD_DIRS); do \
		make --no-print-directory --directory $$DIR pull-save || exit 1; \
	done
	ls -l */*.tar* 2> /dev/null ||:

.PHONY: save
save:                 # Pull Docker base images and save to tar archive
	for DIR in $(BUILD_DIRS); do \
		make --no-print-directory --directory $$DIR save; \
	done
	ls -l */*.tar* 2> /dev/null ||:

.PHONY: build
build: $(BUILD_DIRS)  # Build Docker images

.PHONY: $(BUILD_DIRS)
$(BUILD_DIRS):        # Build Docker images in parallel
	make --no-print-directory --directory=$@

.PHONY: push-stable
push-stable:          # Tag and push stable Docker images
	for DIR in $(STABLE_DIRS); do \
		make --no-print-directory --directory $$DIR push-stable || exit 1; \
	done
	../bin/docker-images "^drtuxwang/.*:stable "

.PHONY: pull
pull-stable:          # Pull stable Docker images
	for DIR in $(STABLE_DIRS); do \
		make --no-print-directory --directory $$DIR pull-stable || exit 1; \
	done
	../bin/docker-images "drtuxwang/.*:stable"

.PHONY: test
test:                 # Run tests
	for DIR in $(TEST_DIRS); do \
		make --no-print-directory --directory $$DIR test; \
	done

.PHONY: version
version:              # Check versions
	@for DIR in $(BUILD_DIRS); do \
		make --no-print-directory --directory $$DIR version || exit 1; \
	done

.PHONY: prune
prune:                # Prune Docker images/containers
	docker system df
	@echo
	df /var/lib/docker
	docker system prune
	@echo
	../bin/docker-images
	@echo
	docker volume ls
	@echo
	docker ps
	@echo
	docker system df
	@echo
	df /var/lib/docker
	@echo
	docker network ls

.PHONY: clean
clean:                # Remove temporary build files
	rm -f docker-image_*

.PHONY: rmi
rmi:                  # Remove Docker images
	for IMAGE in $(PUSH_IMAGES); do \
		docker rmi -f $${IMAGE%:*}:stable ||:; \
	done
	for DIR in $(BUILD_DIRS); do \
		make --no-print-directory --directory $$DIR rmi; \
	done

.PHONY: rmi-base
rmi-base: rmi         # Remove Docker images including base image
	for DIR in $(BUILD_DIRS); do \
		make --no-print-directory --directory $$DIR rmi-base; \
	done

.PHONY: help
help:                 # Show Makefile options
	@grep "^[A-Za-z0-9].*:" $(lastword $(MAKEFILE_LIST))
