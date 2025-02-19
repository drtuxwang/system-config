ifndef HOST
	HOST := $(shell \
		if [ "`hostname | grep ^debian[^.]`" ]; then \
			echo `hostname`.vm; \
		else \
			echo `hostname`.local; \
		fi \
	)
endif

ifdef TAGS
	TAGS := --tags $(TAGS)
endif


.PHONY: default
default: test         # Default

# Debug: "ANSIBLE_DEBUG=1" & "-vvv"
.PHONY: run
run: play             # Run Ansible

.PHONY: test
test:                 # Dryrun Ansible changes
	@bin/ssh-keys.bash $(HOST)
	ansible-playbook --inventory=inventory/my_nodes my_playbook.yaml --limit $(HOST) $(TAGS) --diff --check

.PHONY: play
play:                 # Apply Ansible changes
	@bin/ssh-keys.bash $(HOST)
	ansible-playbook --inventory=inventory/my_nodes my_playbook.yaml --limit $(HOST) $(TAGS) --diff

.PHONY: tags
tags:                 # Show Ansible tags
	@bin/show-tags.bash

.PHONY: help
help:                 # Show Makefile options
	@grep "^[A-Za-z0-9].*:" $(lastword $(MAKEFILE_LIST))
