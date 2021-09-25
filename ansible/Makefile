ifndef HOST
	HOST := `hostname`.local
endif

ifdef TAGS
	TAGS := --tags $(TAGS)
endif


default: test

# Debug: "ANSIBLE_DEBUG=1" & "-vvv"
.PHONY: run
run: play

.PHONY: test
test:         # Dryrun Ansible changes
	ansible-playbook --inventory=inventory/local_nodes local-playbook.yaml --limit $(HOST) $(TAGS) --diff --check

.PHONY: play
play:         # Apply Ansible changes
	ansible-playbook --inventory=inventory/local_nodes local-playbook.yaml --limit $(HOST) $(TAGS) --diff

.PHONY: tags
tags:         # Show Ansible tags
	@bin/show-tags.sh

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
