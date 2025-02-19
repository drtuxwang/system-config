NAME := test-server
CHART_REPO := ./drtuxwang
CHART_NAME := test-server
NAMESPACE ?= default
HOSTNAME ?= test.kube.local
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

HELM_FLAGS := \
	--namespace=$(NAMESPACE) \
	--values values.yaml \
	--set fullnameOverride=$(NAME) \
	--set image.name=$(APP_IMAGE) \
	--set ingress.server.domain=$(HOSTNAME)
ifdef IMAGE_TAG
	HELM_FLAGS += --set image.tag=$(IMAGE_TAG)
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
	@kubectl --namespace=$(NAMESPACE) get Ingress -o wide 2> /dev/null | grep "$(NAME)" | sed -e "s@^@$(NAMESPACE)   Ingress/@" ||:
	@kubectl --namespace=$(NAMESPACE) get Secrets -o wide 2> /dev/null | grep "$(NAME)" | sed -e "s@^@$(NAMESPACE)   Secrets/@" ||:
	@kubectl --namespace=$(NAMESPACE) get all -o wide 2> /dev/null | grep "$(NAME)" | sed -e "s/^/$(NAMESPACE)   /" ||:

.PHONY: list
list:                 # List Helm chart versions
	@grep "name:" $(CHART_REPO)/$(CHART_NAME)/Chart.yaml | awk '{printf("'$(CHART_REPO)'/%s   ", $$2)}'
	@grep "version:" $(CHART_REPO)/$(CHART_NAME)/Chart.yaml | awk '{printf("%s   ", $$2)}'
	@grep "appVersion:" $(CHART_REPO)/$(CHART_NAME)/Chart.yaml | awk '{printf("%s   ", $$2)}'
	@grep "description:" $(CHART_REPO)/$(CHART_NAME)/Chart.yaml | cut -f2- -d" "

.PHONY: version
version: list         # Show Helm chart and app version
	@echo "\033[33m$(CHART_REPO)/$(CHART_NAME)   $(CHART_VERSION)   $(APP_VERSION)\033[0m"

.PHONY: images
images:               # Show Docker images
	@make template | grep image: | sed -e 's/.* //;s/"//g' | sort | uniq

.PHONY: pull
pull:                 # Pull Docker images

.PHONY: save
save: pull            # Pull Docker base image and save to tar archive

.PHONY: template
template:             # Show Helm template
	helm template $(HELM_FLAGS) $(CHART_REPO)/$(CHART_NAME)

.PHONY: check
check:                # Install Helm release dryrun
	$(HELM_INSTALL) $(HELM_FLAGS) $(HELM_RELEASE) $(CHART_REPO)/$(CHART_NAME) --dry-run --debug

.PHONY: install
install:              # Install Helm release
	kubectl get namespace $(NAMESPACE) 2> /dev/null || kubectl create namespace $(NAMESPACE)
	$(HELM_INSTALL) $(HELM_FLAGS) $(HELM_RELEASE) $(CHART_REPO)/$(CHART_NAME)

.PHONY: connect
connect:              # Connect to endpoint
	@echo "\n*** Connecting to Test Server box ***"
	@kubectl --namespace=$(NAMESPACE) exec -it \
		`kubectl --namespace=$(NAMESPACE) get pod | grep $(NAME)-box | awk 'NR==1 {print $$1}'` \
		-- bash -l


.PHONY: uninstall
uninstall:            # Uninstall Helm release
	$(HELM_LIST)
	$(HELM_UNINSTALL) ||:

.PHONY: clean
clean:                # Remove temporary build files

.PHONY: rmi
rmi:                  # Remove Docker images

.PHONY: help
help:                 # Show Makefile options
	@grep "^[A-Za-z0-9].*:" $(lastword $(MAKEFILE_LIST))
