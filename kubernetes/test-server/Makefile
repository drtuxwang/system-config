NAME := test-server
NAMESPACE := default

# Default local port
ifndef LOCALPORT
	LOCALPORT := 8080
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
	@kubectl get PersistentVolumes -o wide 2> /dev/null | grep $(NAME) | sed -e "s@^@PersistentVolumes/@" ||:
	@kubectl get StorageClass -o wide 2> /dev/null | sed -e "s@^@$$StorageClass/@" ||:
	@for RESOURCE in Ingress PersistentVolumeClaims Secrets Serviceaccount; do \
		kubectl --namespace=$(NAMESPACE) get $$RESOURCE -o wide 2> /dev/null | grep "$(NAME)" | sed -e "s@^@$(NAMESPACE)   $$RESOURCE/@" ||:; \
	done
	@kubectl --namespace=$(NAMESPACE) get all -o wide 2> /dev/null | grep "$(NAME)" | sed -e "s/^/$(NAMESPACE)   /" ||:

.PHONY: create
create:               # Create workload
	@echo "\n*** Creating pods ***"
	kubectl get namespace $(NAMESPACE) 2> /dev/null || kubectl create namespace $(NAMESPACE)
	kubectl --namespace=$(NAMESPACE) create -f $(NAME)-secret-tls.yaml ||:
	kubectl --namespace=$(NAMESPACE) create -f $(NAME)-ingress.yaml ||:
	kubectl --namespace=$(NAMESPACE) create -f $(NAME)-service.yaml ||:
	kubectl --namespace=$(NAMESPACE) create -f $(NAME)-headless-service.yaml ||:
	kubectl --namespace=$(NAMESPACE) create -f $(NAME)-statefulset.yaml ||:

.PHONY: forward
forward:              # Forward http to service
	kubectl --namespace=$(NAMESPACE) describe service/$(NAME)
	kubectl --namespace=$(NAMESPACE) port-forward service/$(NAME) $(LOCALPORT):80

.PHONY: delete
delete:               # Delete workload
	@echo "\n*** Removing pods ***"
	kubectl --namespace=$(NAMESPACE) delete -f $(NAME)-statefulset.yaml ||:
	kubectl --namespace=$(NAMESPACE) delete -f $(NAME)-headless-service.yaml ||:
	kubectl --namespace=$(NAMESPACE) delete -f $(NAME)-service.yaml ||:
	kubectl --namespace=$(NAMESPACE) delete -f $(NAME)-ingress.yaml ||:
	kubectl --namespace=$(NAMESPACE) delete -f $(NAME)-secret-tls.yaml ||:

.PHONY: help
help:                 # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
