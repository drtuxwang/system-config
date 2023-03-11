IMAGES := "drtuxwang/.*"

BUILD_DIRS := \
	alpine-3.16 \
	i386-alpine-3.16 \
	alpine-3.15 \
	\
	debian-11 \
	i386-debian-11 \
	debian-10 \
	debian-9 \
	ubuntu-22.04 \
	ubuntu-20.04 \
	ubuntu-18.04 \
	\
	almalinux-9 \
	almalinux-8 \
	centos-7 \
	\
	busybox-1.33 \
	golang-1.19 \
	httpd-2.4 \
	nginx-1.18 \
	python-3.10 \
	registry-2.6 \
	scratch
STABLE_IMAGES := \
	drtuxwang/debian-bash:11-slim \
	drtuxwang/debian-dev:11-slim \
	drtuxwang/debian-docker:11-slim \
	drtuxwang/debian-xfce:11-slim \
	drtuxwang/nginx:1.18-alpine \
	drtuxwang/python-dev:3.10-slim-bullseye \
	drtuxwang/python-full:3.10-slim-bullseye \
	drtuxwang/scratch
TEST_DIRS := \
	python-3.10


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

.PHONY: push-stable
push-stable:         # Tag and push stable Docker images
	for IMAGE in $(STABLE_IMAGES); do \
		echo "docker tag $$IMAGE $${IMAGE%:*}:stable"; \
		docker tag $$IMAGE $${IMAGE%:*}:stable; \
	done
	for IMAGE in $(STABLE_IMAGES); do \
		echo "docker push $$IMAGE"; \
		docker push $$IMAGE; \
		echo "docker push $${IMAGE%:*}:stable"; \
		docker push $${IMAGE%:*}:stable; \
	done
	docker images --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}" | grep "^drtuxwang/.*:stable " | sort

.PHONY: pull
pull-stable:         # Pull stable Docker images
	for IMAGE in $(STABLE_IMAGES); do \
		docker pull $$IMAGE ; \
		docker pull $${IMAGE%:*}:stable ; \
	done
	docker images --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}" | grep "^drtuxwang/.*:stable " | sort

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
