NAMESPACE := default


default: status

.PHONY: create
create:
	@echo "\n*** Creating cronjob ***"
	kubectl --namespace=$(NAMESPACE) create -f batch-crontab.yaml ||:

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	kubectl --namespace=$(NAMESPACE) get cronjobs
	kubectl --namespace=$(NAMESPACE) get jobs
	kubectl --namespace=$(NAMESPACE) get pods

.PHONY: delete
delete:
	@echo "\n*** Removing cronjob ***"
	kubectl --namespace=$(NAMESPACE) delete -f batch-crontab.yaml ||:

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
