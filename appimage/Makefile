BUILD_DIRS := \
	0ad-0.0.26-deb11 \
	0ad-0.0.26-deb12 \
	bash-5.1.4-deb11 \
	bash-5.2.15-deb12 \
	bash-5.2.37-deb13 \
	vlc-3.0.18-deb12 \
	wesnoth-1.14.15-deb11 \
	wesnoth-1.16.8-deb11 \
	wesnoth-1.16.9-deb12


.PHONY: default
default: status       # Default

.PHONY: status
status:               # Status of Appimage builds
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
help:                 # Show Makefile options
	@grep "^[A-Za-z0-9].*:" $(lastword $(MAKEFILE_LIST))
