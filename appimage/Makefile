BUILD_DIRS := \
	bash \
	vlc \
	wesnoth


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
		make --no-print-directory -C $$DIR build || exit 1:; \
	done

.PHONY: clean
clean:                # Remove temporary build files
	for DIR in $(BUILD_DIRS); do \
		make --no-print-directory -C $$DIR clean; \
	done

.PHONY: help
help:                # Show Makefile options
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
