CHART_NAME := concourse
NAMESPACE := default

default: check

.PHONY: check
check:
	helm install -n $(CHART_NAME) \
		--namespace=$(NAMESPACE) \
		--set persistence.enabled=false s\
		table/concourse \
		--dry-run \
		--debug

.PHONY: install
install:
	helm install -n $(CHART_NAME) \
		--namespace=$(NAMESPACE) \
		--set persistence.enabled=false \
		--set postgresql.persistence.enabled=false \
		stable/concourse
	sleep 2
	kubectl --namespace=$(NAMESPACE) get all

.PHONY: upgrade
upgrade:
	helm upgrade $(CHART_NAME) .
	sleep 2
	kubectl --namespace$(NAMESPACE) get all

.PHONY: forward
forward:
	kubectl --namespace $(NAMESPACE) service/concourse-web
	kubectl --namespace $(NAMESPACE) port-forward service/concourse-web 8080:8080

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm ls
	kubectl --namespace=$(NAMESPACE) get all
	kubectl --namespace=concourse-main get all

.PHONY: clean
clean:
	helm ls
	helm del --purge $(CHART_NAME) ||:
	sleep 2
	kubectl delete namespace concourse-main
