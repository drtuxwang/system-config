NAMESPACE := default


default: status

.PHONY: status
status:       # Show workload status
	@echo "\n*** Checking status ***"
	kubectl --namespace=$(NAMESPACE) get cronjobs
	kubectl --namespace=$(NAMESPACE) get jobs
	kubectl --namespace=$(NAMESPACE) get pods

.PHONY: create
create:       # Create workload
	@echo "\n*** Creating cronjob ***"
	kubectl --namespace=$(NAMESPACE) create -f cronjob.yaml ||:

.PHONY: delete
delete:       # Delete workload
	@echo "\n*** Removing cronjob ***"
	kubectl --namespace=$(NAMESPACE) delete -f cronjob.yaml ||:

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
