SERVER := http://kubernetes.local:8080

default: build

build:
	@echo "\n*** Building replicationcontroller ***"
	kubectl -s $(SERVER) create -f ckong-ns.json
	kubectl -s $(SERVER) create -f debian-svc.json
	# kubectl -s $(SERVER) create -f debian-pod.json
	kubectl -s $(SERVER) create -f debian-rc.json

clean:
	@echo "\n*** Building replicationcontroller ***"
	kubectl -s $(SERVER) --namespace=ckong delete rc debian-lxc ||:
	kubectl -s $(SERVER) --namespace=ckong delete service debian-lxc ||:
	kubectl -s $(SERVER) delete namespace ckong ||:

status:
	@echo "\n*** Checking status ***"
	kubectl -s $(SERVER) get namespaces
	kubectl -s $(SERVER) --namespace=ckong get services
	kubectl -s $(SERVER) --namespace=ckong get rc
	kubectl -s $(SERVER) --namespace=ckong get pods

test: pep8
	@echo "\n*** Tests successfull ***"

pep8:
	@echo "\n*** Running JSON PEP8 check ***"
	python3 -m pep8 --max-line-length=255 *.json
