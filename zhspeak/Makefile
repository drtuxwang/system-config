VERSION=$(shell ../bin/zhspeak -h | grep "Zhong Hua Speak v" | sed -e "s/Zhong Hua Speak v//;s/ .*//")

.PHONY: default
default: build        # Default

.PHONY: build
build: clean          # Build zhspeak archive
	@echo "\n*** Building Zhong Hua Speak archive ***"
	git lfs pull -I zhspeak/zhspeak-data.7z
	mkdir -p bin
	cp -p ../bin/zhspeak* \
		../bin/pyld.* \
		../bin/command_mod.py \
		../bin/file_mod.py \
		../bin/subtask_mod.py \
		../bin/task_mod.py bin/
	../bin/un7z zhspeak-data.7z
	../bin/7z zhspeak_${VERSION}_generic.7z bin zhspeak-data
	ls -l zhspeak_${VERSION}_generic.7z

.PHONY: run
test:                 # Run zhspeak tests
	@echo "\n*** Running Zhong Hua Speak tests ***"
	../bin/zhspeak -zh 123
	../bin/zhspeak -zhy 123

.PHONY: run
run:                  # Run zhspeak GUI
	@echo "\n*** Running Zhong Hua Speak GUI ****"
	bin/zhspeak -g &

.PHONY: clean
clean:                # Remove temporary build files
	rm -rf bin zhspeak-data zhspeak_*_generic.7z

.PHONY: help
help:                 # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
