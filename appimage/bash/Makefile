.PHONY: default
default: build test  # Default

.PHONY: status
status:              # Status of AppImage
	@ls -l

.PHONY: build
build:               # Build Docker images
	../bin/build-appimage.sh appimage.yaml

.PHONY: test
test:                # Run tests
	@echo
	./*.AppImage --appimage-help
	@echo
	./*.AppImage --version

.PHONY: clean
clean:               # Remove temporary build files
	rm -rf AppDir appimage-builder-cache *.AppImage

.PHONY: help
help:                # Show Makefile options
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
