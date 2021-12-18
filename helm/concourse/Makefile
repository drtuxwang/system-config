NAME := concourse
CHART_REPO := concourse
CHART_URL := https://concourse-charts.storage.googleapis.com
CHART_NAME := concourse
CHART_VERSION := 15.7.1
NAMESPACE ?= infra
HOSTNAME ?= concourse.kube.local
TLS_SECRET ?= kube-local-tls
LOCALPORT ?=

ifndef APP_VERSION
	APP_VERSION=$(shell make --no-print-directory version | awk 'END {print $$3}')
endif
ifndef INGRESS_ENABLED
	INGRESS_ENABLED=$(shell timeout 2 kubectl get ClusterRoleBinding 2> /dev/null | grep -q ^ingress && echo true || echo false)
endif
EXTERNAL_IP=$(shell ping -c 1 $(HOSTNAME) 2> /dev/null | grep "^PING" | sed -e "s/.* (//;s/).*//")
HELM_FLAGS := \
	--namespace=$(NAMESPACE) \
	--values values.yaml \
	--set fullnameOverride=$(NAME) \
	--set postgresql.fullnameOverride=$(NAME)-postgresql \
	--set service.type=ClusterIP \
	--set web.ingress.enabled=$(INGRESS_ENABLED) \
	--set web.ingress.hosts[0]=$(HOSTNAME) \
	--set web.ingress.secretName=$(TLS_SECRET) \
	--version $(CHART_VERSION)
ifdef IMAGE_TAG
	HELM_FLAGS += --set imageTag=$(IMAGE_TAG)
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


default: status

.PHONY: status
status:       # Status of Helm release
	@echo "\n*** Checking status ***"
	$(HELM_STATUS)
	$(HELM_LIST)

.PHONY: repo-add
repo-add:     # Add Helm repository
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
	kubectl --namespace=$(NAMESPACE) port-forward service/$(NAME)-web $(LOCALPORT):8080

.PHONY: connect
connect:      # Connect to endpoint
	@echo "Username: test"
	@echo "Password: test"
	@if [ "$(EXTERNAL_IP)" ]; then \
		../../kubernetes/bin/kube-connect.sh http://${HOSTNAME}; \
	else \
		../../kubernetes/bin/kube-connect.sh http://$(NAMESPACE)/service/${NAME}-web:8080; \
	fi

.PHONY: uninstall
uninstall:    # Uninstall Helm release
	$(HELM_LIST)
	$(HELM_UNINSTALL) ||:
	sleep 2
	kubectl delete namespace $(NAME)-main ||:

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
