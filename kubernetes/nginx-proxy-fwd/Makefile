ifndef NAMESPACE
	NAMESPACE := default
endif


default: status

.PHONY: create
create:
	@echo "\n*** Creating pods ***"
	kubectl --namespace=$(NAMESPACE) create configmap nginx-proxy-fwd-config \
		--from-file nginx-proxy-fwd.conf
	kubectl --namespace=$(NAMESPACE) create configmap nginx-proxy-fwd-ssl \
		--from-file=proxy-kube-local.crt \
		--from-file=proxy-kube-local.key
	kubectl --namespace=$(NAMESPACE) create -f nginx-proxy-fwd.yaml ||:

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	kubectl --namespace=$(NAMESPACE) get pod -o wide | grep ^nginx-proxy-fwd- ||:
	kubectl --namespace=$(NAMESPACE) get configmap | grep ^nginx-proxy-fwd- ||:

.PHONY: delete
delete:
	@echo "\n*** Removing pods ***"
	kubectl --namespace=$(NAMESPACE) delete -f nginx-proxy-fwd.yaml ||:
	kubectl --namespace=$(NAMESPACE) delete configmap nginx-proxy-fwd-config nginx-proxy-fwd-ssl ||:

.PHONY: mkcert
cert:
	openssl genrsa -out proxy-kube-local.key 2048
	openssl req -new -x509 -nodes -key proxy-kube-local.key -out proxy-kube-local.crt -days 365 -subj /CN=proxy.kube.local
	openssl x509 -enddate -text -noout -in proxy-kube-local.crt

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
