NAMESPACE := default


.PHONY: default
default: status      # Default

.PHONY: status
status:              # Show workload status
	@echo "\n*** Checking status ***"
	kubectl --namespace=$(NAMESPACE) get all -o wide
	@echo
	kubectl --namespace=$(NAMESPACE) get pvc
	@echo
	kubectl --namespace=$(NAMESPACE) get pv
	@echo
	kubectl --namespace=$(NAMESPACE) get sc

.PHONY: create
create:              # Create workload
	@echo "\n*** Creating pods ***"
	kubectl create namespace $(NAMESPACE) ||:
	kubectl --namespace=$(NAMESPACE) create -f server-pv.yaml ||:
	kubectl --namespace=$(NAMESPACE) create -f server-statefulset.yaml ||:

.PHONY: delete
delete:              # Delete workload
	@echo "\n*** Removing pods ***"
	kubectl --namespace=$(NAMESPACE) delete -f server-statefulset.yaml ||:
	kubectl --namespace=$(NAMESPACE) delete pvc data-server-0
	kubectl --namespace=$(NAMESPACE) delete -f server-pv.yaml ||:

.PHONY: help
help:                # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
