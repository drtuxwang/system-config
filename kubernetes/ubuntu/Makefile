NAMESPACE := ubuntu

default: build

.PHONY: build
build:
	@echo "\n*** Creating pods ***"
	kubectl create -f namespace-ubuntu.yaml
	kubectl --namespace=$(NAMESPACE) create -f service-ubuntu.yaml
	kubectl --namespace=$(NAMESPACE) create -f service-ubuntu-headless.yaml
	kubectl --namespace=$(NAMESPACE) create -f statefulset-ubuntu.yaml
	# kubectl --namespace=$(NAMESPACE) create -f daemonset-ubuntu.yaml
	# kubectl --namespace=$(NAMESPACE) create -f deployment-ubuntu.yaml
	# kubectl --namespace=$(NAMESPACE) create -f replicationcontroller-ubuntu.yaml
	# kubectl --namespace=$(NAMESPACE) create -f pod-ubuntu.yaml

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
	kubectl get namespaces
	kubectl --namespace=$(NAMESPACE) get services
	kubectl --namespace=$(NAMESPACE) get rc
	kubectl --namespace=$(NAMESPACE) get deploy
	kubectl --namespace=$(NAMESPACE) get ds
	kubectl --namespace=$(NAMESPACE) get statefulset
	kubectl --namespace=$(NAMESPACE) get pods
