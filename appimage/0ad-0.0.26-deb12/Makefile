.PHONY: default
default: build test  # Default

.PHONY: status
status:              # Status of AppImage
	@ls -l

.PHONY: build
build:               # Build Docker images
	../bin/build-appimage.bash AppImageBuilder.yaml

.PHONY: test
test:                # Run tests
	@echo
	./*.AppImage --appimage-help ||:
	@echo
	../bin/check-debs.bash AppImageBuilder.yaml
	@echo
	./*.AppImage --version
	@echo
	ls -l *.AppImage

.PHONY: clean
clean:               # Remove temporary build files
	rm -rf AppDir appimage-build *.AppImage *.zsync

.PHONY: help
help:                # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
