.PHONY: default
default: build        # Default

.PHONY: build
build:                # Build executable
	gcc -O3 wipe.c -o wipe
	ls -l wipe
	strip wipe
	ls -l wipe

.PHONY: clean
clean:                # Remove temporary build files
	rm -f wipe

.PHONY: help
help:                 # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
