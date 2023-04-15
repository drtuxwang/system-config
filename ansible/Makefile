ifndef HOST
	HOST := `hostname`.local
endif

ifdef TAGS
	TAGS := --tags $(TAGS)
endif


.PHONY: default
default: test        # Default

# Debug: "ANSIBLE_DEBUG=1" & "-vvv"
.PHONY: run
run: play            # Run Ansible

.PHONY: test
test:                # Dryrun Ansible changes
	@bin/ssh-keys.bash $(HOST)
	ansible-playbook --inventory=inventory/local_nodes local-playbook.yaml --limit $(HOST) $(TAGS) --diff --check

.PHONY: play
play:                # Apply Ansible changes
	@bin/ssh-keys.bash $(HOST)
	ansible-playbook --inventory=inventory/local_nodes local-playbook.yaml --limit $(HOST) $(TAGS) --diff

.PHONY: tags
tags:                # Show Ansible tags
	@bin/show-tags.bash

.PHONY: help
help:                # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
