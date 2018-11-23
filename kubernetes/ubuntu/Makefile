NAMESPACE := test

default: build

.PHONY: build
build:
	@echo "\n*** Creating pods ***"
	kubectl create -f test-ns.yaml
	# kubectl --namespace=$(NAMESPACE) create -f ubuntu-svc.yaml
	kubectl --namespace=$(NAMESPACE) create -f ubuntu-svc.yaml
	kubectl --namespace=$(NAMESPACE) create -f ubuntu-headless-svc.yaml
	kubectl --namespace=$(NAMESPACE) create -f ubuntu-statefulset.yaml
	# kubectl --namespace=$(NAMESPACE) create -f ubuntu-ds.yaml
	# kubectl --namespace=$(NAMESPACE) create -f ubuntu-deploy.yaml
	# kubectl --namespace=$(NAMESPACE) create -f ubuntu-rc.yaml
	# kubectl --namespace=$(NAMESPACE) create -f ubuntu-pod.yaml

.PHONY: clean
clean:
	@echo "\n*** Removing pods ***"
	kubectl --namespace=$(NAMESPACE) delete -f ubuntu-statefulset.yaml ||:
	kubectl --namespace=$(NAMESPACE) delete -f ubuntu-headless-svc.yaml ||:
	kubectl delete namespace $(NAMESPACE) ||:

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
