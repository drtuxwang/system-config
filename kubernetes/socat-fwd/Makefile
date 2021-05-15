ifndef NAMESPACE
	NAMESPACE := default
endif


default: status

.PHONY: create
create:
	@echo "\n*** Creating pods ***"
	kubectl --namespace=$(NAMESPACE) create -f socat-fwd.yaml ||:

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	kubectl --namespace=$(NAMESPACE) get pod -o wide | grep ^socat-fwd- ||:
	kubectl --namespace=$(NAMESPACE) get configmap | grep ^socat-fwd- ||:

.PHONY: delete
delete:
	@echo "\n*** Removing pods ***"
	kubectl --namespace=$(NAMESPACE) delete -f socat-fwd.yaml ||:

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
