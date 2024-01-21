VERSION=$(shell ../bin/zhspeak -h | grep "Zhong Hua Speak v" | sed -e "s/Zhong Hua Speak v//;s/ .*//")

.PHONY: default
default: archive      # Default

.PHONY: build
build: clean          # Build zhspeak archive
	@echo "\n*** Building Zhong Hua Speak archive ***"
	git lfs pull -I zhspeak/*.7z
	mkdir -p build/bin build/zhspeak-data
	cp -p ../bin/zhspeak* \
		../bin/pyld.* \
		../bin/command_mod.py \
		../bin/file_mod.py \
		../bin/subtask_mod.py \
		../bin/task_mod.py build/bin/
	cp -p README.md build/zhspeak-data/
	cd build/zhspeak-data && ../../../bin/un7z ../../*.7z
	build/bin/zhspeak

.PHONY: run
test:                 # Run zhspeak tests
	@echo "\n*** Running Zhong Hua Speak tests ***"
	build/bin/zhspeak -zh 123
	build/bin/zhspeak -zhy 123

.PHONY: archive
archive: build test   # Create release archive
	@echo "\n*** Creating Zhong Hua Speak release archive ***"
	cd build && ../../bin/7z zhspeak_${VERSION}_generic.7z
	@echo "\nRelease archive:"
	@ls -l build/zhspeak_${VERSION}_generic.7z

.PHONY: run
run:                  # Run zhspeak GUI
	@echo "\n*** Running Zhong Hua Speak GUI ****"
	bin/zhspeak -g &

.PHONY: clean
clean:                # Remove temporary build files
	rm -rf build

.PHONY: help
help:                 # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
