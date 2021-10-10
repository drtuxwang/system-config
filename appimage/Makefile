BUILD_DIRS := \
	bash \
	vlc \
	wesnoth


.PHONY: default
default: status

.PHONY: status
status:
	@for DIR in $(BUILD_DIRS); do \
		ls -l $$DIR/*.AppImage ||:; \
	done

.PHONY: build
build:
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR build || exit 1:; \
	done

.PHONY: clean
clean:
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR clean; \
	done

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
