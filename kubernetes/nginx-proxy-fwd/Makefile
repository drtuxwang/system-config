NAME := nginx-proxy-fwd

ifndef NAMESPACE
	NAMESPACE := default
endif


.PHONY: default
default: status      # Default

.PHONY: status
status:              # Show workload status
	@echo "\n*** Checking Kube status ***"
	@make --no-print-directory status-kube | sort
	@echo

.PHONY: status-kube
status-kube:         # Show Kube workload status
	@kubectl --namespace=$(NAMESPACE) get ConfigMap -o wide 2> /dev/null | grep "$(NAME)" | sed -e "s@^@$(NAMESPACE)   ConfigMap/@" ||:
	@kubectl --namespace=$(NAMESPACE) get all -o wide 2> /dev/null | grep "$(NAME)" | sed -e "s/^/$(NAMESPACE)   /" ||:

.PHONY: create-cert
create-cert:         # Create https certificate
	openssl genrsa -out proxy-kube-local.key 2048
	openssl req -new -x509 -nodes -key proxy-kube-local.key -out proxy-kube-local.crt -days 365 -subj /CN=proxy.kube.local
	openssl x509 -enddate -text -noout -in proxy-kube-local.crt

.PHONY: create
create:              # Create workload
	@echo "\n*** Creating pods ***"
	kubectl --namespace=$(NAMESPACE) create configmap $(NAME)-config \
		--from-file $(NAME).conf
	kubectl --namespace=$(NAMESPACE) create configmap $(NAME)-ssl \
		--from-file=proxy-kube-local.crt \
		--from-file=proxy-kube-local.key
	kubectl --namespace=$(NAMESPACE) create -f $(NAME).yaml ||:

.PHONY: delete
delete:              # Delete workload
	@echo "\n*** Removing pods ***"
	kubectl --namespace=$(NAMESPACE) delete -f $(NAME).yaml ||:
	kubectl --namespace=$(NAMESPACE) delete configmap $(NAME)-config $(NAME)-ssl ||:

.PHONY: clean
clean:               # Remove temporary build files
	rm proxy-kube-local.crt proxy-kube-local.key

.PHONY: help
help:                # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
