NAMESPACE := servers-test

default: status

.PHONY: build
build:
	@echo "\n*** Creating pods ***"
	kubectl create namespace $(NAMESPACE) ||:
	kubectl --namespace=$(NAMESPACE) create -f servers-secret-tls.yaml ||:
	kubectl --namespace=$(NAMESPACE) create -f servers-ingress.yaml ||:
	kubectl --namespace=$(NAMESPACE) create -f servers-service.yaml ||:
	kubectl --namespace=$(NAMESPACE) create -f servers-headless-service.yaml ||:
	kubectl --namespace=$(NAMESPACE) create -f servers-statefulset.yaml ||:

.PHONY: forward
forward:
	kubectl --namespace=$(NAMESPACE) describe service/server
	kubectl --namespace=$(NAMESPACE) port-forward service/server 8080:80

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
	kubectl --namespace=$(NAMESPACE) delete -f servers-statefulset.yaml ||:
	kubectl --namespace=$(NAMESPACE) delete -f servers-headless-service.yaml ||:
	kubectl --namespace=$(NAMESPACE) delete -f servers-service.yaml ||:
	kubectl --namespace=$(NAMESPACE) create -f servers-ingress.yaml ||:
	kubectl --namespace=$(NAMESPACE) create -f servers-secret-tls.yaml ||:
