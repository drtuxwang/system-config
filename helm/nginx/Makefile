NAME := nginx
CHART_REPO := bitnami
CHART_URL := https://charts.bitnami.com/bitnami
CHART_NAME := nginx
CHART_VERSION := 9.4.3
APP_VERSION := 1.18.0
IMAGE_TAG := 1.18.0-debian-10-r363
HOSTNAME ?= nginx.kube.local
NAMESPACE ?= default
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
	--set ingress.enabled=$(INGRESS_ENABLED) \
	--set ingress.hosts\[0\].name=$(HOSTNAME) \
	--set ingress.hostname=$(HOSTNAME) \
	--set service.type=ClusterIP \
	--version $(CHART_VERSION)
ifdef IMAGE_TAG
	HELM_FLAGS += --set image.tag=$(IMAGE_TAG)
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

.PHONY: repo-add
repo-add:
	helm repo list | grep -q $(CHART_REPO) || helm repo add $(CHART_REPO) $(CHART_URL)

.PHONY: fetch
fetch: repo-add clean
	mkdir $(CHART_REPO) && \
		cd $(CHART_REPO) && \
		helm fetch --untar --version=$(CHART_VERSION) $(CHART_REPO)/$(CHART_NAME)

.PHONY: images
images:
	@make template | grep image: | sed -e 's/.* //;s/"//g' | sort | uniq

.PHONY: pull
pull:
	@for IMAGE in `make --no-print-directory images`; do \
		docker pull $$IMAGE; \
	done

.PHONY: save
save:
	../bin/helm-save \
		$(CHART_REPO)-$(CHART_NAME) \
		$(CHART_VERSION) \
		$(APP_VERSION) \
		$(shell make --no-print-directory images)

.PHONY: template
template: repo-add
	helm template \
		$(HELM_FLAGS) \
		$(CHART_REPO)/$(CHART_NAME)

.PHONY: check
check: repo-add
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		$(HELM_FLAGS) \
		$(HELM_RELEASE) $(CHART_REPO)/$(CHART_NAME)

.PHONY: install
install: repo-add
	kubectl get namespace $(NAMESPACE) || kubectl create namespace $(NAMESPACE)
	helm upgrade \
		--install \
		--wait \
		$(HELM_FLAGS) \
		$(HELM_RELEASE) $(CHART_REPO)/$(CHART_NAME)

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	$(HELM_STATUS)
	$(HELM_LIST)

.PHONY: forward
forward:
	kubectl --namespace=$(NAMESPACE) port-forward service/$(NAME) $(LOCALPORT):80

.PHONY: connect
connect:
	@if [ "$(EXTERNAL_IP)" ]; then \
		../../kubernetes/bin/kube-connect http://${HOSTNAME}; \
	else \
		../../kubernetes/bin/kube-connect http://$(NAMESPACE)/service/${NAME}; \
	fi

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
	rm -rf $(CHART_REPO)

.PHONY: rmi
rmi:
	@for IMAGE in `make --no-print-directory images`; do \
		docker rmi -f $$IMAGE ||:; \
	done

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
