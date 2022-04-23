NAMESPACE := default


default: status

.PHONY: status
status:       # Show workload status
	@echo "\n*** Checking status ***"
	kubectl --namespace=$(NAMESPACE) get all -o wide
	@echo
	kubectl --namespace=$(NAMESPACE) get pvc
	@echo
	kubectl --namespace=$(NAMESPACE) get pv
	@echo
	kubectl --namespace=$(NAMESPACE) get sc

.PHONY: create
create:       # Create workload
	@echo "\n*** Creating pods ***"
	kubectl create namespace $(NAMESPACE) ||:
	kubectl --namespace=$(NAMESPACE) create -f local-storageclass.yaml ||:
	kubectl --namespace=$(NAMESPACE) create -f data-server-persistentvolume.yaml ||:
	kubectl --namespace=$(NAMESPACE) create -f server-statefulset.yaml ||:

.PHONY: delete
delete:       # Delete workload
	@echo "\n*** Removing pods ***"
	kubectl --namespace=$(NAMESPACE) delete -f server-statefulset.yaml ||:
	kubectl --namespace=$(NAMESPACE) delete pvc data-server-0 ||:
	kubectl --namespace=$(NAMESPACE) delete -f data-server-persistentvolume.yaml ||:

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))