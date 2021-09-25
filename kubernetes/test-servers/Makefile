NAMESPACE := default

# Default local port
ifndef LOCALPORT
	LOCALPORT := 8080
endif


default: status

.PHONY: status
status:       # Show workload status
	@echo "\n*** Checking status ***"
	kubectl --namespace=$(NAMESPACE) get all -o wide
	@echo
	kubectl --namespace=$(NAMESPACE) get secrets -o wide
	@echo
	kubectl --namespace=$(NAMESPACE) get ingress -o wide
	@echo
	kubectl --namespace=$(NAMESPACE) get serviceaccount
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
	kubectl --namespace=$(NAMESPACE) create -f servers-secret-tls.yaml ||:
	kubectl --namespace=$(NAMESPACE) create -f servers-ingress.yaml ||:
	kubectl --namespace=$(NAMESPACE) create -f servers-service.yaml ||:
	kubectl --namespace=$(NAMESPACE) create -f servers-headless-service.yaml ||:
	kubectl --namespace=$(NAMESPACE) create -f servers-statefulset.yaml ||:

.PHONY: forward
forward:      # Forward http to service
	kubectl --namespace=$(NAMESPACE) describe service/server
	kubectl --namespace=$(NAMESPACE) port-forward service/server $(LOCALPORT):80

.PHONY: delete
delete:       # Delete workload
	@echo "\n*** Removing pods ***"
	kubectl --namespace=$(NAMESPACE) delete -f servers-statefulset.yaml ||:
	kubectl --namespace=$(NAMESPACE) delete -f servers-headless-service.yaml ||:
	kubectl --namespace=$(NAMESPACE) delete -f servers-service.yaml ||:
	kubectl --namespace=$(NAMESPACE) delete -f servers-ingress.yaml ||:
	kubectl --namespace=$(NAMESPACE) delete -f servers-secret-tls.yaml ||:

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
