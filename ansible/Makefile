ifndef HOST
	HOST := `hostname`.local
endif


default: test

# Debug: "ANSIBLE_DEBUG=1"  & "-vvv"
.PHONY: test
test:
	ansible-playbook --inventory=inventory/local_cluster setup-local.yaml --limit $(HOST) --diff --check

.PHONY: run
run:
	ansible-playbook --inventory=inventory/local_cluster setup-local.yaml --limit $(HOST) --diff

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
