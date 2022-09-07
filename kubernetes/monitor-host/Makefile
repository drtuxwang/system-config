ifndef NAMESPACE
	NAMESPACE := default
endif


.PHONY: default
default: status      # Default

.PHONY: status
status:              # Show workload status
	@echo "\n*** Checking status ***"
	kubectl --namespace=$(NAMESPACE) get pod -o wide | grep ^monitor-host- ||:

.PHONY: create
create:              # Create workload
	@echo "\n*** Creating pods ***"
	kubectl --namespace=$(NAMESPACE) create -f monitor-host-daemonset.yaml ||:

.PHONY: delete
delete:              # Delete workload
	@echo "\n*** Removing pods ***"
	kubectl --namespace=$(NAMESPACE) delete -f monitor-host-daemonset.yaml ||:

.PHONY: help
help:                # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
