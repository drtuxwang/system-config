IMAGES := "drtuxwang/.*"

BUILD_DIRS := \
	alpine-3.17 \
	i386-alpine-3.17 \
	alpine-3.16 \
	\
	debian-12 \
	i386-debian-12 \
	debian-11 \
	i386-debian-11 \
	debian-10 \
	ubuntu-22.04 \
	ubuntu-20.04 \
	ubuntu-18.04 \
	\
	almalinux-9 \
	almalinux-8 \
	oraclelinux-9 \
	oraclelinux-8 \
	centos-7 \
	\
	busybox-1.34 \
	golang-1.19 \
	httpd-2.4 \
	nginx-1.18 \
	python-3.11 \
	registry-2.6 \
	scratch
STABLE_DIRS := \
	debian-12/bash \
	debian-12/dev \
	debian-12/docker \
	debian-12/xfce \
	nginx-1.18 \
	python-3.11/dev \
	python-3.11/full \
	scratch
TEST_DIRS := \
	python-3.11


.PHONY: default
default: build status # Default

.PHONY: status
status:              # Status of Docker images
	docker images --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}" | grep "^$(IMAGES):" | sort
	docker system df

.PHONY: new
new:                 # Create new Docker project
	python3 -m cookiecutter ../cookiecutter/docker

.PHONY: check-base
check-base:          # Show base Docker images
	grep "^BASE_IMAGE" */Makefile

.PHONY: pull
pull:                # Pull base Docker images
	for DIR in $(BUILD_DIRS); do \
		make --no-print-directory --directory $$DIR pull || exit 1; \
	done

.PHONY: pull-save
pull-save:           # Pull base Docker images and save as tar file if changed
	for DIR in $(BUILD_DIRS); do \
		make --no-print-directory --directory $$DIR pull-save || exit 1; \
	done
	ls -l *.tar* 2> /dev/null ||:

.PHONY: save
save:                # Save base Docker images as tar files
	for DIR in $(BUILD_DIRS); do \
		make --no-print-directory --directory $$DIR save; \
	done
	ls -l *.tar* 2> /dev/null ||:

.PHONY: build
build: $(BUILD_DIRS) # Build Docker images

.PHONY: $(BUILD_DIRS)
$(BUILD_DIRS):       # Build Docker images in parallel
	make --no-print-directory --directory=$@

.PHONY: push-stable
push-stable:         # Tag and push stable Docker images
	for DIR in $(STABLE_DIRS); do \
		make --no-print-directory --directory $$DIR push-stable || exit 1; \
	done
	docker images --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}" | grep "^drtuxwang/.*:stable " | sort

.PHONY: pull
pull-stable:         # Pull stable Docker images
	for DIR in $(STABLE_DIRS); do \
		make --no-print-directory --directory $$DIR pull-stable || exit 1; \
	done
	docker images --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}" | grep "^drtuxwang/.*:stable " | sort

.PHONY: test
test:                # Run tests
	for DIR in $(TEST_DIRS); do \
		make --no-print-directory --directory $$DIR test; \
	done

.PHONY: version
version:             # Check versions
	@for DIR in $(BUILD_DIRS); do \
		make --no-print-directory --directory $$DIR version || exit 1; \
	done

.PHONY: prune
prune:               # Prune Docker images/containers
	docker system df
	@echo
	df /var/lib/docker
	docker system prune
	@echo
	docker images --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}"
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
clean:               # Remove temporary build files
	rm -f docker-image_*

.PHONY: rmi
rmi:                 # Remove Docker images
	for IMAGE in $(PUSH_IMAGES); do \
		docker rmi -f $${IMAGE%:*}:stable ||:; \
	done
	for DIR in $(BUILD_DIRS); do \
		make --no-print-directory --directory $$DIR rmi; \
	done

.PHONY: rmi-base
rmi-base: rmi        # Remove Docker images including base image
	for DIR in $(BUILD_DIRS); do \
		make --no-print-directory --directory $$DIR rmi-base; \
	done

.PHONY: help
help:                # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
