ifndef NAMESPACE
	NAMESPACE := default
endif


.PHONY: default
default: status      # Default

.PHONY: status
status:              # Show workload status
	@echo "\n*** Checking status ***"
	kubectl --namespace=$(NAMESPACE) get pod -o wide | grep ^socat-fwd- ||:
	kubectl --namespace=$(NAMESPACE) get configmap | grep ^socat-fwd- ||:

.PHONY: create
create:              # Create workload
	@echo "\n*** Creating pods ***"
	kubectl --namespace=$(NAMESPACE) create -f socat-fwd.yaml ||:

.PHONY: delete
delete:              # Delete workload
	@echo "\n*** Removing pods ***"
	kubectl --namespace=$(NAMESPACE) delete -f socat-fwd.yaml ||:

.PHONY: help
help:                # Show Makefile options
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
