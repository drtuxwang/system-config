NAME := prometheus
CHART_REPO := prometheus-community
CHART_NAME := prometheus
CHART_VERSION := 11.14.1

# Default namespace
ifndef NAMESPACE
	NAMESPACE=infra
endif

# Default local port
ifndef LOCALPORT
	LOCALPORT=
endif

# Ingress controller detection
INGRESS_ENABLED=$(shell kubectl get ClusterRoleBinding 2> /dev/null | grep -q ^ingress && echo true || echo false)

default: status

.PHONY: fetch
fetch:
	helm fetch --version=$(CHART_VERSION) $(CHART_REPO)/$(CHART_NAME)
	rm -rf $(CHART_NAME)
	tar xf $(CHART_NAME)-$(CHART_VERSION).tgz

.PHONY: check
check:
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set alertmanager.fullnameOverride=$(NAME)-alertmanager \
		--set kube-state-metrics.fullnameOverride=$(NAME)-kube-state-metrics \
		--set nodeExporter.fullnameOverride=$(NAME)-nodeexporter \
		--set pushgateway.fullnameOverride=$(NAME)-pushgateway \
		--set server.fullnameOverride=$(NAME)-server \
		--set server.ingress.enabled=$(INGRESS_ENABLED) \
		--version $(CHART_VERSION) \
		$(NAMESPACE)-$(NAME) $(CHART_REPO)/$(CHART_NAME)

.PHONY: install
install:
	echo debugX $(INGRESS_ENABLED)
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set alertmanager.fullnameOverride=$(NAME)-alertmanager \
		--set kube-state-metrics.fullnameOverride=$(NAME)-kube-state-metrics \
		--set nodeExporter.fullnameOverride=$(NAME)-nodeexporter \
		--set pushgateway.fullnameOverride=$(NAME)-pushgateway \
		--set server.fullnameOverride=$(NAME)-server \
		--set server.ingress.enabled=$(INGRESS_ENABLED) \
		--version $(CHART_VERSION) \
		$(NAMESPACE)-$(NAME) $(CHART_REPO)/$(CHART_NAME)

.PHONY: forward
forward:
	kubectl --namespace=$(NAMESPACE) port-forward service/$(NAME)-server $(LOCALPORT):80

.PHONY: connect
connect:
	./connect.sh

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	@if [ "`helm version | grep v2`" ]; then \
		helm status $(NAMESPACE)-$(NAME); \
		helm ls $(NAMESPACE)-$(NAME); \
	else \
		helm status -n $(NAMESPACE) $(NAMESPACE)-$(NAME); \
		helm list -n $(NAMESPACE) --all; \
	fi

.PHONY: version
version:
	@if [ "`helm version | grep v2`" ]; then \
		helm search -l $(CHART_REPO)/$(CHART_NAME) | tail -n +2 | \
			grep -B 1000 "^$(CHART_REPO)/$(CHART_NAME)[	 ]*$(CHART_VERSION) " | \
			sed -e "s/	/   /g" -e "s/   */   /g"; \
	else \
		helm search repo -l $(CHART_REPO)/$(CHART_NAME) | tail -n +2 | \
			grep -B 1000 "^$(CHART_REPO)/$(CHART_NAME)[	 ]*$(CHART_VERSION) " | \
			sed -e "s/	/   /g" -e "s/   */   /g"; \
	fi

.PHONY: uninstall
uninstall:
	@if [ "`helm version | grep v2`" ]; then \
		helm ls $(NAMESPACE)-$(NAME); \
		helm del --purge $(NAMESPACE)-$(NAME) ||:; \
	else \
		helm list -n $(NAMESPACE) --all; \
		helm uninstall -n $(NAMESPACE) $(NAMESPACE)-$(NAME) ||:; \
	fi

.PHONY: clean
clean:
	rm -rf $(CHART_NAME)-*.tgz $(CHART_NAME)
