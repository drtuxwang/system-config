NAME := test-cronjob
NAMESPACE := default


.PHONY: default
default: status      # Default

.PHONY: status
status:              # Show workload status
	@echo "\n*** Checking Kube status ***"
	@make --no-print-directory status-kube | sort
	@echo

.PHONY: status-kube
status-kube:         # Show Kube workload status
	@kubectl --namespace=$(NAMESPACE) get all -o wide 2> /dev/null | grep "$(NAME)" | sed -e "s/^/$(NAMESPACE)   /" ||:

.PHONY: create
create:              # Create workload
	@echo "\n*** Creating cronjob ***"
	kubectl --namespace=$(NAMESPACE) create -f test-cronjob.yaml ||:

.PHONY: delete
delete:              # Delete workload
	@echo "\n*** Removing cronjob ***"
	kubectl --namespace=$(NAMESPACE) delete -f test-cronjob.yaml ||:

.PHONY: help
help:                # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
