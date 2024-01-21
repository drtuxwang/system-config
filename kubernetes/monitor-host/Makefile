NAME := monitor-host

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
	@kubectl --namespace=$(NAMESPACE) get all -o wide 2> /dev/null | grep "$(NAME)" | sed -e "s/^/$(NAMESPACE)   /" ||:

.PHONY: create
create:               # Create workload
	@echo "\n*** Creating pods ***"
	kubectl --namespace=$(NAMESPACE) create -f $(NAME)-daemonset.yaml ||:

.PHONY: delete
delete:               # Delete workload
	@echo "\n*** Removing pods ***"
	kubectl --namespace=$(NAMESPACE) delete -f $(NAME)-daemonset.yaml ||:

.PHONY: help
help:                 # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
