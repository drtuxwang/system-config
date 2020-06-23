ifndef NAMESPACE
	NAMESPACE=default
endif


default: status

.PHONY: create
create:
	@echo "\n*** Creating pods ***"
	kubectl --namespace=$(NAMESPACE) create -f monitor-host-daemonset.yaml ||:

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	kubectl --namespace=$(NAMESPACE) get pod -o wide | grep ^monitor-host- ||:

.PHONY: delete
delete:
	@echo "\n*** Removing pods ***"
	kubectl --namespace=$(NAMESPACE) delete -f monitor-host-daemonset.yaml ||:
