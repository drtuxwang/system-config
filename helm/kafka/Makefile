NAME := kafka
CHART_REPO := bitnami
CHART_URL := https://charts.bitnami.com/bitnami
CHART_NAME := kafka
CHART_VERSION := 12.3.2
NAMESPACE ?= default
HOSTNAME ?= kafka.kube.local

ifndef APP_VERSION
	APP_VERSION=$(shell make --no-print-directory version | awk 'END {print $$3}')
endif
EXTERNAL_IP=$(shell ping -c 1 $(HOSTNAME) 2> /dev/null | grep "^PING" | sed -e "s/.* (//;s/).*//")
HELM_FLAGS := \
	--namespace=$(NAMESPACE) \
	--values values.yaml \
	--set fullnameOverride=$(NAME)-server \
	--set zookeeper.fullnameOverride=$(NAME)-zookeeper \
	--set externalAccess.service.domain=$(EXTERNAL_IP) \
	--version $(CHART_VERSION)
ifeq ($(shell echo ${EXTERNAL_IP} | grep -c "^."), 1)
	HELM_FLAGS += --set service.externalIPs='{$(EXTERNAL_IP)}'
endif
ifdef IMAGE_TAG
	HELM_FLAGS += --set image.tag=$(IMAGE_TAG)
endif
ifeq ($(shell helm version | grep -c v2), 1)
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

.PHONY: connect
connect:
	@if [ "$(EXTERNAL_IP)" ]; then \
		./test-connect.sh $(NAME)-server-0 \
			$(EXTERNAL_IP):`kubectl get svc kafka-server-0-external | awk 'NR==2 {print $$5}' | sed -e "s/.*://;s#/.*##"`; \
	else \
		./test-connect.sh $(NAME)-server-0 \
			127.0.0.1:`kubectl get svc kafka-server-0-external | awk 'NR==2 {print $$5}' | cut -f1 -d:`; \
	fi

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
	rm -rf $(CHART_REPO)

.PHONY: rmi
rmi:
	@for IMAGE in `make --no-print-directory images`; do \
		docker rmi -f $$IMAGE ||:; \
	done

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
