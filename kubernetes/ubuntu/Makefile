SERVER := http://kubernetes.local:8080
NAMESPACE := default

default: build

.PHONY: build
build:
	@echo "\n*** Building replicationcontroller ***"
	kubectl -s $(SERVER) create -f test-ns.yml
	kubectl -s $(SERVER) create -f ubuntu-svc.yml
	# kubectl -s $(SERVER) create -f ubuntu-pod.yml
	# kubectl -s $(SERVER) create -f ubuntu-rc.yml
	kubectl -s $(SERVER) create -f ubuntu-deploy.yml
	# kubectl -s $(SERVER) create -f ubuntu-ds.yml
	# kubectl -s $(SERVER) create -f ubuntu-statefulset.yml

.PHONY: clean
clean:
	@echo "\n*** Building replicationcontroller ***"
	kubectl -s $(SERVER) --namespace=$(NAMESPACE) delete deploy ubuntu-lxc ||:
	kubectl -s $(SERVER) --namespace=$(NAMESPACE) delete service ubuntu-lxc ||:
	kubectl -s $(SERVER) delete namespace $(NAMESPACE) ||:

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	kubectl -s $(SERVER) get namespaces
	kubectl -s $(SERVER) --namespace=$(NAMESPACE) get services
	kubectl -s $(SERVER) --namespace=$(NAMESPACE) get rc
	kubectl -s $(SERVER) --namespace=$(NAMESPACE) get deploy
	kubectl -s $(SERVER) --namespace=$(NAMESPACE) get ds
	kubectl -s $(SERVER) --namespace=$(NAMESPACE) get statefulset
	kubectl -s $(SERVER) --namespace=$(NAMESPACE) get pods
