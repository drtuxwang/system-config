NAMESPACE := ubuntu

default: build

.PHONY: build
build:
	@echo "\n*** Creating pods ***"
	kubectl create -f namespace-ubuntu.yaml
	kubectl --namespace=$(NAMESPACE) create -f service-ubuntu.yaml
	kubectl --namespace=$(NAMESPACE) create -f service-ubuntu-headless.yaml
	kubectl --namespace=$(NAMESPACE) create -f statefulset-ubuntu.yaml

.PHONY: clean
clean:
	@echo "\n*** Removing pods ***"
	kubectl --namespace=$(NAMESPACE) delete -f statefulset-ubuntu.yaml ||:
	kubectl --namespace=$(NAMESPACE) delete -f service-ubuntu-headless.yaml ||:
	kubectl --namespace=$(NAMESPACE) delete -f service-ubuntu.yaml ||:
	kubectl delete -f namespace-ubuntu.yaml ||:

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	kubectl --namespace=$(NAMESPACE) get all
