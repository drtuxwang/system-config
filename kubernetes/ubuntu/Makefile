SERVER := http://kubernetes.local:8080
NAMESPACE := default

default: build

build:
	@echo "\n*** Building replicationcontroller ***"
	kubectl -s $(SERVER) create -f test-ns.json
	kubectl -s $(SERVER) create -f ubuntu-svc.json
	# kubectl -s $(SERVER) create -f ubuntu-pod.json
	kubectl -s $(SERVER) create -f ubuntu-rc.json

clean:
	@echo "\n*** Building replicationcontroller ***"
	kubectl -s $(SERVER) --namespace=$(NAMESPACE) delete rc ubuntu-lxc ||:
	kubectl -s $(SERVER) --namespace=$(NAMESPACE) delete service ubuntu-lxc ||:
	kubectl -s $(SERVER) delete namespace $(NAMESPACE) ||:

status:
	@echo "\n*** Checking status ***"
	kubectl -s $(SERVER) get namespaces
	kubectl -s $(SERVER) --namespace=$(NAMESPACE) get services
	kubectl -s $(SERVER) --namespace=$(NAMESPACE) get rc
	kubectl -s $(SERVER) --namespace=$(NAMESPACE) get pods

test: pep8
	@echo "\n*** Tests successfull ***"

pep8:
	@echo "\n*** Running JSON PEP8 check ***"
	python3 -m pep8 --max-line-length=255 *.json
