NAME := cassandra
CHART_REPO := bitnami
CHART_URL := https://charts.bitnami.com/bitnami
CHART_NAME := cassandra
CHART_VERSION := 7.7.3
NAMESPACE ?= infra
LOCALPORT ?=

ifndef APP_VERSION
	APP_VERSION=$(shell make --no-print-directory version | awk 'END {print $$3}')
endif
HELM_FLAGS := \
	--namespace=$(NAMESPACE) \
	--values values.yaml \
	--set fullnameOverride=$(NAME) \
	--set service.type=ClusterIP \
	--version $(CHART_VERSION)
ifdef IMAGE_TAG
	HELM_FLAGS += --set image.tag=$(IMAGE_TAG)
endif
ifeq ($(shell timeout 2 helm version 2> /dev/null | grep -c v2), 1)
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


default: status

.PHONY: status
status:       # Status of Helm release
	$(HELM_STATUS)
	$(HELM_LIST)

.PHONY: repo-add
repo-add:     # Add Helm repository
	@echo "\n*** Checking status ***"
	helm repo list | grep -q $(CHART_REPO) || helm repo add $(CHART_REPO) $(CHART_URL)

.PHONY: version
version:      # Helm chart versions
	@$(HELM_VERSION) | tail -n +2 | \
		grep -B 1000 "^$(CHART_REPO)/$(CHART_NAME)[	 ]*$(CHART_VERSION) " | \
		sed -e "s/	/   /g" -e "s/   */   /g"

.PHONY: fetch
fetch: repo-add clean  # Fetch Helm chart
	mkdir $(CHART_REPO) && \
		cd $(CHART_REPO) && \
		helm fetch --untar --version=$(CHART_VERSION) $(CHART_REPO)/$(CHART_NAME)

.PHONY: images
images:       # Show Docker images
	@INGRESS_ENABLED=false make template | grep image: | sed -e 's/.* //;s/"//g' | sort | uniq

.PHONY: pull
pull:         # Pull Docker images
	@for IMAGE in `make --no-print-directory images`; do \
		docker pull $$IMAGE; \
	done

.PHONY: save
save:         # Save Docker images as tar file
	../bin/helm-save.sh \
		$(CHART_REPO)-$(CHART_NAME) \
		$(CHART_VERSION) \
		$(APP_VERSION) \
		$(shell make --no-print-directory images)

.PHONY: template
template: repo-add  # Show Helm template
	helm template \
		$(HELM_FLAGS) \
		$(CHART_REPO)/$(CHART_NAME)

.PHONY: check
check: repo-add  # Dryrun Helm install
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		$(HELM_FLAGS) \
		$(HELM_RELEASE) $(CHART_REPO)/$(CHART_NAME)

.PHONY: install
install: repo-add  # Install Helm release
	kubectl get namespace $(NAMESPACE) || kubectl create namespace $(NAMESPACE)
	helm upgrade \
		--install \
		--wait \
		$(HELM_FLAGS) \
		$(HELM_RELEASE) $(CHART_REPO)/$(CHART_NAME)

.PHONY: forward
forward:      # Forward traffic to endpoint
	kubectl --namespace=$(NAMESPACE) port-forward service/$(NAME) $(LOCALPORT):80

.PHONY: connect
connect:      # Connect to endpoint
	@CASSANDRA_SECRET=cassandra ../../kubernetes/bin/kube-connect.sh cql://$(NAMESPACE)/service/${NAME}:9042

.PHONY: uninstall
uninstall:    # Uninstall Helm release
	$(HELM_LIST)
	$(HELM_UNINSTALL) ||:

.PHONY: clean
clean:        # Remove temporary build files
	rm -rf $(CHART_REPO)

.PHONY: rmi
rmi:          # Remove Docker images
	@for IMAGE in `make --no-print-directory images`; do \
		docker rmi -f $$IMAGE ||:; \
	done

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
