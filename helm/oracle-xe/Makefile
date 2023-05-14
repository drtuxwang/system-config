NAME := oracle-xe
CHART_REPO := ./drtuxwang
CHART_NAME := oracle-xe
NAMESPACE ?= infra
HOSTNAME ?= oracle.kube.local
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
HELM_FLAGS := \
	--namespace=$(NAMESPACE) \
	--values values.yaml \
	--set image.name=$(APP_IMAGE) \
	--set fullnameOverride=$(NAME)
ifeq ($(shell echo ${EXTERNAL_IP} | grep -c "^."), 1)
	HELM_FLAGS += --set service.externalIPs='{$(EXTERNAL_IP)}'
endif
ifdef IMAGE_TAG
	HELM_FLAGS += --set image.tag=$(IMAGE_TAG)
endif


.PHONY: default
default: status      # Default

.PHONY: status
status:              # Show workload status
	@echo "\n*** Checking Helm release status ***"
	@make --no-print-directory status-helm
	@echo "\n*** Checking Kube status ***"
	@make --no-print-directory status-kube | sort
	@echo

.PHONY: status-helm
status-helm:         # Show Helm release status
	$(HELM_STATUS) ||:
	$(HELM_LIST)

.PHONY: status-kube
status-kube:         # Show Kube workload status
	@kubectl --namespace=$(NAMESPACE) get all -o wide 2> /dev/null | grep "$(NAME)" | sed -e "s/^/$(NAMESPACE)   /" ||:

.PHONY: list
list:                # List Helm chart versions
	@grep "name:" $(CHART_REPO)/$(CHART_NAME)/Chart.yaml | awk '{printf("'$(CHART_REPO)'/%s   ", $$2)}'
	@grep "version:" $(CHART_REPO)/$(CHART_NAME)/Chart.yaml | awk '{printf("%s   ", $$2)}'
	@grep "appVersion:" $(CHART_REPO)/$(CHART_NAME)/Chart.yaml | awk '{printf("%s   ", $$2)}'
	@grep "description:" $(CHART_REPO)/$(CHART_NAME)/Chart.yaml | cut -f2- -d" "

.PHONY: version
version: list        # Show Helm chart and app version
	@echo "\033[33m$(CHART_REPO)/$(CHART_NAME)   $(CHART_VERSION)   $(APP_VERSION)\033[0m"

.PHONY: images
images:              # Show Docker images
	@make template | grep image: | sed -e 's/.* //;s/"//g' | sort | uniq

.PHONY: pull
pull:                # Pull Docker images
	@for IMAGE in `make --no-print-directory images`; do \
		docker pull $$IMAGE; \
	done

.PHONY: save
save:                # Save Docker images as tar file
	../bin/helm-save.bash \
		$(CHART_REPO)-$(CHART_NAME) \
		$(CHART_VERSION) \
		$(APP_VERSION) \
		$(shell make --no-print-directory images)

.PHONY: template
template:            # Show Helm template
	helm template $(HELM_FLAGS) $(CHART_REPO)/$(CHART_NAME)

.PHONY: check
check:               # Install Helm release dryrun
	$(HELM_INSTALL) $(HELM_FLAGS) $(HELM_RELEASE) $(CHART_REPO)/$(CHART_NAME) --dry-run --debug

.PHONY: install
install:             # Install Helm release
	kubectl get namespace $(NAMESPACE) 2> /dev/null || kubectl create namespace $(NAMESPACE)
	$(HELM_INSTALL) $(HELM_FLAGS) $(HELM_RELEASE) $(CHART_REPO)/$(CHART_NAME)

.PHONY: forward
forward:             # Forward traffic to endpoint
	kubectl --namespace=$(NAMESPACE) port-forward service/$(NAME)-box $(LOCALPORT):1521

.PHONY: connect
connect:             # Connect to endpoint
	@echo "\n*** Connecting to Oracle XE database ***"
	@if [ "$(EXTERNAL_IP)" ]; \
	then \
		../../kubernetes/bin/kube-connect.bash oradb://${HOSTNAME}:1521; \
	else \
		../../kubernetes/bin/kube-connect.bash oradb://$(NAMESPACE)/service/${NAME}-box:1521; \
	fi

.PHONY: uninstall
uninstall:           # Uninstall Helm release
	$(HELM_LIST)
	$(HELM_UNINSTALL) ||:

.PHONY: clean
clean:               # Remove temporary build files

.PHONY: rmi
rmi:                 # Remove Docker images
	@for IMAGE in `make --no-print-directory images`; do \
		docker rmi -f $$IMAGE ||:; \
	done

.PHONY: help
help:                # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
