NAME := nginx-proxy-fwd

ifndef NAMESPACE
	NAMESPACE := default
endif


.PHONY: default
default: status       # Default

.PHONY: status
status:               # Show workload status
	@echo "\n*** Checking Kube status ***"
	@make --no-print-directory status-kube | sort
	@echo

.PHONY: status-kube
status-kube:          # Show Kube workload status
	@kubectl --namespace=$(NAMESPACE) get ConfigMap -o wide 2> /dev/null | grep "$(NAME)" | sed -e "s@^@$(NAMESPACE)   ConfigMap/@" ||:
	@kubectl --namespace=$(NAMESPACE) get all -o wide 2> /dev/null | grep "$(NAME)" | sed -e "s/^/$(NAMESPACE)   /" ||:

.PHONY: create-cert
create-cert:          # Create https certificate
	openssl genrsa -out proxy-kube-local.key 2048
	openssl req -new -x509 -nodes -key proxy-kube-local.key -out proxy-kube-local.crt -days 365 -subj /CN=proxy.kube.local
	openssl x509 -enddate -text -noout -in proxy-kube-local.crt

.PHONY: create
create:               # Create workload
	@echo "\n*** Creating pods ***"
	kubectl --namespace=$(NAMESPACE) create configmap $(NAME)-config \
		--from-file $(NAME).conf
	kubectl --namespace=$(NAMESPACE) create configmap $(NAME)-ssl \
		--from-file=proxy-kube-local.crt \
		--from-file=proxy-kube-local.key
	kubectl --namespace=$(NAMESPACE) create -f $(NAME).yaml ||:

.PHONY: test
test:                 # Test TLS
	@echo "\n*** Test TLS 1 fails ***"
	openssl s_client -connect localhost:8443 -tls1 < /dev/null && exit 1 ||:
	@echo "\n*** Test TLS 1.1 fails ***"
	openssl s_client -connect localhost:8443 -tls1_1 < /dev/null && exit 1 ||:
	@echo "\n*** Test TLS 1.2 works ***"
	openssl s_client -connect localhost:8443 -tls1_2 < /dev/null
	@echo "\n*** Test TLS 1.3 works ***"
	openssl s_client -connect localhost:8443 -tls1_3 < /dev/null
	@echo "\n*** Test redirection ***"
	curl http://localhost:8080 | grep "BBC Homepage"
	curl --insecure https://localhost:8443 | grep "BBC Homepage"

.PHONY: delete
delete:               # Delete workload
	@echo "\n*** Removing pods ***"
	kubectl --namespace=$(NAMESPACE) delete -f $(NAME).yaml ||:
	kubectl --namespace=$(NAMESPACE) delete configmap $(NAME)-config $(NAME)-ssl ||:

.PHONY: clean
clean:                # Remove temporary build files
	rm proxy-kube-local.crt proxy-kube-local.key

.PHONY: help
help:                 # Show Makefile options
	@grep "^[A-Za-z0-9].*:" $(lastword $(MAKEFILE_LIST))
