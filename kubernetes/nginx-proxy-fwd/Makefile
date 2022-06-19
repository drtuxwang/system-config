ifndef NAMESPACE
	NAMESPACE := default
endif


.PHONY: default
default: status      # Default

.PHONY: status
status:              # Show workload status
	@echo "\n*** Checking status ***"
	kubectl --namespace=$(NAMESPACE) get pod -o wide | grep ^nginx-proxy-fwd- ||:
	kubectl --namespace=$(NAMESPACE) get configmap | grep ^nginx-proxy-fwd- ||:

.PHONY: mkcert
cert:                # Create https certificate
	openssl genrsa -out proxy-kube-local.key 2048
	openssl req -new -x509 -nodes -key proxy-kube-local.key -out proxy-kube-local.crt -days 365 -subj /CN=proxy.kube.local
	openssl x509 -enddate -text -noout -in proxy-kube-local.crt

.PHONY: create
create:              # Create workload
	@echo "\n*** Creating pods ***"
	kubectl --namespace=$(NAMESPACE) create configmap nginx-proxy-fwd-config \
		--from-file nginx-proxy-fwd.conf
	kubectl --namespace=$(NAMESPACE) create configmap nginx-proxy-fwd-ssl \
		--from-file=proxy-kube-local.crt \
		--from-file=proxy-kube-local.key
	kubectl --namespace=$(NAMESPACE) create -f nginx-proxy-fwd.yaml ||:

.PHONY: delete
delete:              # Delete workload
	@echo "\n*** Removing pods ***"
	kubectl --namespace=$(NAMESPACE) delete -f nginx-proxy-fwd.yaml ||:
	kubectl --namespace=$(NAMESPACE) delete configmap nginx-proxy-fwd-config nginx-proxy-fwd-ssl ||:

.PHONY: clean
clean:               # Remove temporary build files
	rm proxy-kube-local.crt proxy-kube-local.key

.PHONY: help
help:                # Show Makefile options
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
