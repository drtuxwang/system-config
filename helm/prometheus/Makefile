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
ifndef INGRESS_ENABLED
	INGRESS_ENABLED=$(shell kubectl get ClusterRoleBinding 2> /dev/null | grep -q ^ingress && echo true || echo false)
endif

ifeq ($(shell helm version | grep -c v2), 1)
	HELM_LIST=helm list --all $(NAMESPACE)-$(NAME)
	HELM_STATUS=helm status $(NAMESPACE)-$(NAME)
	HELM_UNINSTALL=helm delete --purge $(NAMESPACE)-$(NAME)
	HELM_VERSION=helm search -l $(CHART_REPO)/$(CHART_NAME)
else
	HELM_LIST=helm list -n $(NAMESPACE) --all | grep $(NAMESPACE)-$(NAME)
	HELM_STATUS=helm status -n $(NAMESPACE) $(NAMESPACE)-$(NAME)
	HELM_UNINSTALL=helm uninstall -n $(NAMESPACE) $(NAMESPACE)-$(NAME)
	HELM_VERSION=helm search repo -l $(CHART_REPO)/$(CHART_NAME)
endif

IMAGES_FILE=../helm-images_$(CHART_NAME)-$(CHART_VERSION)_app-$(shell make --no-print-directory version | awk 'END {print $$3}').tar

default: status


.PHONY: repo-add
repo-add:
	helm repo list | grep -q prometheus-community || helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

.PHONY: fetch
fetch: repo-add
	helm fetch --version=$(CHART_VERSION) $(CHART_REPO)/$(CHART_NAME)
	rm -rf $(CHART_NAME)
	tar xf $(CHART_NAME)-$(CHART_VERSION).tgz

.PHONY: images
images:
	@INGRESS_ENABLED=false make template | grep image: | sed -e 's/.* //;s/"//g' | sort | uniq

.PHONY: pull
pull:
	@for IMAGE in `make --no-print-directory images`; do \
		docker pull $$IMAGE; \
	done

.PHONY: save
save:
	../helm-save.sh $(IMAGES_FILE) $(shell make --no-print-directory images)

.PHONY: template
template: repo-add
	helm template \
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
		$(CHART_REPO)/$(CHART_NAME)

.PHONY: check
check: repo-add
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
install: repo-add
	kubectl get namespace $(NAMESPACE) || kubectl create namespace $(NAMESPACE)
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
	$(HELM_STATUS)
	$(HELM_LIST)

.PHONY: version
version:
	@$(HELM_VERSION) | tail -n +2 | \
		grep -B 1000 "^$(CHART_REPO)/$(CHART_NAME)[	 ]*$(CHART_VERSION) " | \
		sed -e "s/	/   /g" -e "s/   */   /g"

.PHONY: uninstall
uninstall:
	$(HELM_LIST)
	$(HELM_UNINSTALL) ||:

.PHONY: clean
clean:
	rm -rf $(CHART_NAME)-*.tgz $(CHART_NAME)
