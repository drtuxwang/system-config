ifndef NAMESPACE
	NAMESPACE=default
endif


default: status

.PHONY: build
install:
	@echo "\n*** Creating pods ***"
	kubectl --namespace=$(NAMESPACE) create -f monitor-node-daemonset.yaml ||:

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	kubectl --namespace=$(NAMESPACE) get pod -o wide | grep monitor-node- ||:

.PHONY: clean
clean:
	@echo "\n*** Removing pods ***"
	kubectl --namespace=$(NAMESPACE) delete -f monitor-node-daemonset.yaml ||:
