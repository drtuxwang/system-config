.PHONY: default
default: build       # Default

.PHONY: build
build:               # Build executable
	./COMPILE

.PHONY: clean
clean:                # Remove temporary build files
	rm -f wipe

.PHONY: help
help:                # Show Makefile options
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
