NAMESPACE := linux-test

default: status

.PHONY: build
build:
	@echo "\n*** Creating pods ***"
	kubectl create namespace $(NAMESPACE) ||:
	kubectl --namespace=$(NAMESPACE) create -f secret-linux.yaml ||:
	kubectl --namespace=$(NAMESPACE) create -f ingress-linux.yaml ||:
	kubectl --namespace=$(NAMESPACE) create -f service-linux.yaml ||:
	kubectl --namespace=$(NAMESPACE) create -f service-linux-headless.yaml ||:
	kubectl --namespace=$(NAMESPACE) create -f statefulset-linux.yaml ||:

.PHONY: forward
forward:
	kubectl --namespace=$(NAMESPACE) describe service/linux
	kubectl --namespace=$(NAMESPACE) port-forward service/linux 8080:80

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	kubectl --namespace=$(NAMESPACE) get all -o wide
	@echo
	kubectl --namespace=$(NAMESPACE) get secrets -o wide
	@echo
	kubectl --namespace=$(NAMESPACE) get ingress -o wide

.PHONY: clean
clean:
	@echo "\n*** Removing pods ***"
	kubectl --namespace=$(NAMESPACE) delete -f statefulset-linux.yaml ||:
	kubectl --namespace=$(NAMESPACE) delete -f service-linux-headless.yaml ||:
	kubectl --namespace=$(NAMESPACE) delete -f service-linux.yaml ||:
	kubectl --namespace=$(NAMESPACE) create -f ingress-linux.yaml ||:
	kubectl --namespace=$(NAMESPACE) create -f secret-linux.yaml ||:
