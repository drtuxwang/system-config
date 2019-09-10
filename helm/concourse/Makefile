NAME := concourse
NAMESPACE := default

# Default local port
ifndef LOCALPORT
	LOCALPORT=8080
endif

default: status

.PHONY: check
check:
	helm repo add stable https://kubernetes-charts.storage.googleapis.com
	helm install -n $(NAME) \
		--namespace=$(NAMESPACE) \
		--set persistence.enabled=false \
		stable/concourse \
		--dry-run \
		--debug

.PHONY: install
install:
	helm repo add stable https://kubernetes-charts.storage.googleapis.com
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

.PHONY: forward
forward:
	kubectl --namespace $(NAMESPACE) port-forward service/concourse-web $(LOCALPORT):8080

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm ls
	@echo
	kubectl --namespace=$(NAMESPACE) get all -o wide

.PHONY: clean
clean:
	helm ls
	helm del --purge $(CHART_NAME) ||:
	sleep 2
	kubectl delete namespace concourse-main
