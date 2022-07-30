NAME := ops-server
CHART_REPO := ./drtuxwang
CHART_NAME := ops-server
NAMESPACE ?= default

ifndef CHART_VERSION
	CHART_VERSION=$(shell make --no-print-directory list | awk 'END {print $$2}')
endif
ifndef APP_VERSION
	APP_VERSION=$(shell make --no-print-directory list | awk 'END {print $$3}')
endif
ifeq ($(shell timeout 2 helm version | grep -c v2), 1)
	HELM_RELEASE := $(NAMESPACE)-$(NAME)
	HELM_LIST := helm list --all $(HELM_RELEASE)
	HELM_STATUS := helm status $(HELM_RELEASE)
	HELM_UNINSTALL := helm delete --purge $(HELM_RELEASE)
	HELM_VERSION := helm search -l $(CHART_REPO)/$(CHART_NAME)
else
	HELM_RELEASE :=$(NAME)
	HELM_LIST := helm --namespace=$(NAMESPACE) list --all | grep $(HELM_RELEASE)
	HELM_STATUS := helm --namespace=$(NAMESPACE) status $(HELM_RELEASE)
	HELM_UNINSTALL := helm --namespace=$(NAMESPACE) uninstall $(HELM_RELEASE)
	HELM_VERSION := helm search repo -l $(CHART_REPO)/$(CHART_NAME)
endif

HELM_FLAGS := \
	--namespace=$(NAMESPACE) \
	--values values.yaml \
	--set image.name=$(APP_IMAGE) \
	--set fullnameOverride=$(NAME)
ifdef IMAGE_TAG
	HELM_FLAGS += --set image.tag=$(IMAGE_TAG)
endif


.PHONY: default
default: status      # Default

.PHONY: status
status:              # Status of Helm release
	@echo "\n*** Checking status ***"
	$(HELM_STATUS)
	$(HELM_LIST)

.PHONY: list
list:                # List Helm chart versions
	@grep "name:" $(CHART_REPO)/$(CHART_NAME)/Chart.yaml | awk '{printf("./'$(CHART_NAME)'/%s   ", $$2)}'
	@grep "version:" $(CHART_REPO)/$(CHART_NAME)/Chart.yaml | awk '{printf("%s   ", $$2)}'
	@grep "appVersion:" $(CHART_REPO)/$(CHART_NAME)/Chart.yaml | awk '{printf("%s   ", $$2)}'
	@grep "description:" $(CHART_REPO)/$(CHART_NAME)/Chart.yaml | cut -f2- -d" "

.PHONY: version
version: list        # Show Helm chart and app version
	@echo "Helm Chart: $(CHART_REPO)/$(CHART_NAME) $(CHART_VERSION) (app-$(APP_VERSION))"

.PHONY: images
images:              # Show Docker images
	@make template | grep image: | sed -e 's/.* //;s/"//g' | sort | uniq

.PHONY: pull
pull:                # Pull Docker images

.PHONY: save
save:                # Save Docker images as tar file

.PHONY: template
template:            # Show Helm template
	helm template \
		$(HELM_FLAGS) \
		$(CHART_REPO)/$(CHART_NAME)

.PHONY: check
check:               # Dryrun Helm install
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		$(HELM_FLAGS) \
		$(HELM_RELEASE) $(CHART_REPO)/$(CHART_NAME)

.PHONY: install
install:             # Install Helm release
	kubectl get namespace $(NAMESPACE) || kubectl create namespace $(NAMESPACE)
	helm upgrade \
		--install \
		--wait \
		$(HELM_FLAGS) \
		$(HELM_RELEASE) $(CHART_REPO)/$(CHART_NAME)

.PHONY: connect
connect:             # Connect to endpoint
	@echo "\n*** Connecting to Ops box ***"
	@kubectl --namespace=$(NAMESPACE) exec -it \
		`kubectl --namespace=$(NAMESPACE) get pod | grep $(NAME)-box | awk 'NR==1 {print $$1}'` \
		-- bash -l

.PHONY: uninstall
uninstall:           # Uninstall Helm release
	$(HELM_LIST)
	$(HELM_UNINSTALL) ||:

.PHONY: clean
clean:               # Remove temporary build files

.PHONY: rmi
rmi:                 # Remove Docker images

.PHONY: help
help:                # Show Makefile options
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
