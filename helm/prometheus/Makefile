NAME := prometheus
CHART_REPO := prometheus-community
CHART_URL := https://prometheus-community.github.io/helm-charts
CHART_NAME := prometheus
CHART_VERSION := 27.7.1
APP_VERSION := 2.53.4
IMAGE_TAG := v2.53.4
NAMESPACE ?= infra
HOSTNAME ?= prometheus.kube.local
LOCALPORT ?=

ifndef CHART_VERSION
	CHART_VERSION=$(shell make --no-print-directory list | awk 'END {print $$2}')
endif
ifndef APP_VERSION
	APP_VERSION=$(shell make --no-print-directory list | awk 'END {print $$3}')
endif
ifeq ($(shell timeout 2 helm version 2> /dev/null | grep -c v2), 1)
	HELM_RELEASE := $(NAMESPACE)-$(NAME)
	HELM_LIST := helm list --all $(HELM_RELEASE)
	HELM_VERSION := helm search -l $(CHART_REPO)/$(CHART_NAME)
	HELM_STATUS := helm status $(HELM_RELEASE)
	HELM_UNINSTALL := helm delete --purge $(HELM_RELEASE)
else
	HELM_RELEASE := $(NAME)
	HELM_LIST := helm --namespace=$(NAMESPACE) list --all | grep $(HELM_RELEASE)
	HELM_VERSION := helm search repo -l $(CHART_REPO)/$(CHART_NAME)
	HELM_STATUS := helm --namespace=$(NAMESPACE) status $(HELM_RELEASE)
	HELM_UNINSTALL := helm --namespace=$(NAMESPACE) uninstall $(HELM_RELEASE)
endif
HELM_INSTALL := helm upgrade --install --wait

EXTERNAL_IP=$(shell ping -c 1 $(HOSTNAME) 2> /dev/null | grep "^PING" | sed -e "s/.* (//;s/).*//")
ifndef INGRESS_ENABLED
	INGRESS_ENABLED=$(shell timeout 2 kubectl get ClusterRoleBinding 2> /dev/null | grep -Eq "^ingress|traefik" && echo true || echo false)
endif
HELM_FLAGS := \
	--namespace=$(NAMESPACE) \
	--values values.yaml \
	--set fullnameOverride=$(NAME) \
	--set alertmanager.fullnameOverride=$(NAME)-alertmanager \
	--set kube-state-metrics.fullnameOverride=$(NAME)-kube-state-metrics \
	--set nodeExporter.fullnameOverride=$(NAME)-nodeexporter \
	--set pushgateway.fullnameOverride=$(NAME)-pushgateway \
	--set server.fullnameOverride=$(NAME)-server \
	--set server.ingress.enabled=$(INGRESS_ENABLED) \
	--set server.ingress.hosts[0]=$(HOSTNAME) \
	--version $(CHART_VERSION)
ifdef IMAGE_TAG
	HELM_FLAGS += --set server.image.tag=$(IMAGE_TAG)
endif


.PHONY: default
default: status       # Default

.PHONY: status
status:               # Show workload status
	@echo "\n*** Checking Helm release status ***"
	@make --no-print-directory status-helm
	@echo "\n*** Checking Kube status ***"
	@make --no-print-directory status-kube | sort
	@echo

.PHONY: status-helm
status-helm:          # Show Helm release status
	$(HELM_STATUS) ||:
	$(HELM_LIST)

.PHONY: status-kube
status-kube:          # Show Kube workload status
	@kubectl get ClusterRole -o wide 2> /dev/null | grep "$(NAME)" | sed -e "s@^@ClusterRole/@" ||:
	@kubectl get ClusterRoleBinding -o wide 2> /dev/null | grep "$(NAME)" | sed -e "s@^@ClusterRoleBinding/@" ||:
	@for RESOURCE in ConfigMap Ingress ServiceAccount; do \
		kubectl --namespace=$(NAMESPACE) get $$RESOURCE -o wide 2> /dev/null | grep "$(NAME)" | sed -e "s@^@$(NAMESPACE)   $$RESOURCE/@" ||:; \
	done
	@kubectl --namespace=$(NAMESPACE) get all -o wide 2> /dev/null | grep "$(NAME)" | sed -e "s/^/$(NAMESPACE)   /" ||:

.PHONY: repo-add
repo-add:             # Add Helm repository
	helm repo list | grep -q $(CHART_REPO) || helm repo add $(CHART_REPO) $(CHART_URL)

.PHONY: list
list:                 # List Helm chart versions
	@$(HELM_VERSION) | grep "^$(CHART_REPO)/$(CHART_NAME)[	 ]" | \
		sed -e "s/	/   /g;s/   */   /g" | sed '0,/ $(CHART_VERSION) /!d'

.PHONY: version
version: list         # Show Helm chart and app version
	@echo "\033[33m$(CHART_REPO)/$(CHART_NAME)   $(CHART_VERSION)   $(APP_VERSION)\033[0m"

.PHONY: fetch
fetch: repo-add clean # Fetch Helm chart
	mkdir $(CHART_REPO) && \
		cd $(CHART_REPO) && \
		helm fetch --untar --version=$(CHART_VERSION) $(CHART_REPO)/$(CHART_NAME)

.PHONY: images
images:               # Show Docker images
	@make template | grep image: | sed -e 's/.* //;s/"//g' | sort | uniq

.PHONY: pull
pull:                 # Pull Docker images
	@for IMAGE in `make --no-print-directory images`; do \
		docker pull $$IMAGE; \
	done

.PHONY: save
save: pull            # Pull Docker base image and save to tar archive
	../bin/helm-save.bash \
		$(CHART_REPO)-$(CHART_NAME) \
		$(CHART_VERSION) \
		$(APP_VERSION) \
		$(shell make --no-print-directory images)

.PHONY: template
template: repo-add    # Show Helm template
	helm template $(HELM_FLAGS) $(CHART_REPO)/$(CHART_NAME)

.PHONY: check
check: repo-add       # Install Helm release dryrun
	$(HELM_INSTALL) $(HELM_FLAGS) $(HELM_RELEASE) $(CHART_REPO)/$(CHART_NAME) --dry-run --debug

.PHONY: install
install: repo-add     # Install Helm release
	kubectl get namespace $(NAMESPACE) 2> /dev/null || kubectl create namespace $(NAMESPACE)
	$(HELM_INSTALL) $(HELM_FLAGS) $(HELM_RELEASE) $(CHART_REPO)/$(CHART_NAME)

.PHONY: forward
forward:              # Forward traffic to endpoint
	kubectl --namespace=$(NAMESPACE) port-forward service/$(NAME)-server $(LOCALPORT):80

.PHONY: connect
connect:              # Connect to endpoint
	@if [ "$(EXTERNAL_IP)" ]; \
	then \
		../../kubernetes/bin/kube-connect.bash http://${HOSTNAME}; \
	else \
		../../kubernetes/bin/kube-connect.bash http://$(NAMESPACE)/service/${NAME}-server; \
	fi

.PHONY: uninstall
uninstall:            # Uninstall Helm release
	$(HELM_LIST)
	$(HELM_UNINSTALL) ||:

.PHONY: clean
clean:                # Remove temporary build files
	rm -rf $(CHART_REPO)

.PHONY: rmi
rmi:                  # Remove Docker images
	@for IMAGE in `make --no-print-directory images`; do \
		docker rmi -f $$IMAGE ||:; \
	done

.PHONY: help
help:                 # Show Makefile options
	@grep "^[A-Za-z0-9].*:" $(lastword $(MAKEFILE_LIST))
