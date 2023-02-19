BUILD_DIRS := \
	0ad-0.0.26 \
	bash-5.1.4 \
	wesnoth-1.14.15 \
	wesnoth-1.16.8


.PHONY: default
default: status      # Default

.PHONY: status
status:              # Status of Appimage builds
	@for DIR in $(BUILD_DIRS); do \
		ls -l $$DIR/*.AppImage 2> /dev/null ||:; \
	done

.PHONY: build
build:                # Build Appimage images
	for DIR in $(BUILD_DIRS); do \
		make --no-print-directory --directory $$DIR build || exit 1:; \
	done

.PHONY: clean
clean:                # Remove temporary build files
	for DIR in $(BUILD_DIRS); do \
		make --no-print-directory --directory $$DIR clean; \
	done

.PHONY: help
help:                # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
