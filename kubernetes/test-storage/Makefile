NAME := test-storage
NAMESPACE := default


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
	@kubectl --namespace=$(NAMESPACE) get PersistentVolumeClaims -o wide 2> /dev/null | grep "$(NAME)" | sed -e "s@^@$(NAMESPACE)   PersistentVolumeClaims/@" ||:
	@kubectl --namespace=$(NAMESPACE) get all -o wide 2> /dev/null | grep "$(NAME)" | sed -e "s/^/$(NAMESPACE)   /" ||:

.PHONY: create
create:               # Create workload
	@echo "\n*** Creating pods ***"
	kubectl get namespace $(NAMESPACE) 2> /dev/null || kubectl create namespace $(NAMESPACE)
	kubectl --namespace=$(NAMESPACE) create -f $(NAME)-pv.yaml ||:
	kubectl --namespace=$(NAMESPACE) create -f $(NAME)-statefulset.yaml ||:

.PHONY: delete
delete:               # Delete workload
	@echo "\n*** Removing pods ***"
	kubectl --namespace=$(NAMESPACE) delete -f $(NAME)-statefulset.yaml ||:
	kubectl --namespace=$(NAMESPACE) delete pvc data-$(NAME)-0
	kubectl --namespace=$(NAMESPACE) delete -f $(NAME)-pv.yaml ||:

.PHONY: help
help:                 # Show Makefile options
	@grep "^[A-Za-z0-9].*:" $(lastword $(MAKEFILE_LIST))
