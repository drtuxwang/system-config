NAME := kafka
CHART_REPO := bitnami
CHART_URL := https://charts.bitnami.com/bitnami
CHART_NAME := kafka
CHART_VERSION := 11.7.2

# Default namespace
ifndef NAMESPACE
	NAMESPACE=default
endif

# External IP
ifndef EXTERNAL_IP
	EXTERNAL_IP=$(shell ping -c 1 kafka.kube.local | grep "^PING" | sed -e "s/.* (//;s/).*//")
endif
ifndef EXTERNAL_IP
    EXTERNAL_IP=$(shell kubectl get nodes -o wide | awk 'NR==2{print $$6}')
endif

ifeq ($(shell helm version | grep -c v2), 1)
	HELM_RELEASE=$(NAMESPACE)-$(NAME)
	HELM_LIST=helm list --all $(HELM_RELEASE)
	HELM_STATUS=helm status $(HELM_RELEASE)
	HELM_UNINSTALL=helm delete --purge $(HELM_RELEASE)
	HELM_VERSION=helm search -l $(CHART_REPO)/$(CHART_NAME)
else
	HELM_RELEASE=$(NAME)
	HELM_LIST=helm --namespace=$(NAMESPACE) list --all | grep $(HELM_RELEASE)
	HELM_STATUS=helm --namespace=$(NAMESPACE) status $(HELM_RELEASE)
	HELM_UNINSTALL=helm --namespace=$(NAMESPACE) uninstall $(HELM_RELEASE)
	HELM_VERSION=helm search repo -l $(CHART_REPO)/$(CHART_NAME)
endif

VERSION=$(shell make --no-print-directory version | awk 'END {print $$3}')
IMAGES_FILE=$(CHART_REPO)-$(CHART_NAME)-$(CHART_VERSION)_app-$(VERSION)_chart-images.tar

default: status


.PHONY: repo-add
repo-add:
	helm repo list | grep -q $(CHART_REPO) || helm repo add $(CHART_REPO) $(CHART_URL)

.PHONY: fetch
fetch: repo-add
	helm fetch --version=$(CHART_VERSION) $(CHART_REPO)/$(CHART_NAME)
	rm -rf $(CHART_NAME)
	tar xf $(CHART_NAME)-$(CHART_VERSION).tgz

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
	../helm-save.sh ../$(IMAGES_FILE) $(shell make --no-print-directory images)

.PHONY: template
template: repo-add
	helm template \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME)-server \
		--set zookeeper.fullnameOverride=$(NAME)-zookeeper \
		--set externalAccess.service.domain=$(EXTERNAL_IP) \
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
		--set fullnameOverride=$(NAME)-server \
		--set zookeeper.fullnameOverride=$(NAME)-zookeeper \
		--set externalAccess.service.domain=$(EXTERNAL_IP) \
		--version $(CHART_VERSION) \
		$(HELM_RELEASE) $(CHART_REPO)/$(CHART_NAME)

.PHONY: install
install: repo-add
	kubectl get namespace $(NAMESPACE) || kubectl create namespace $(NAMESPACE)
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME)-server \
		--set zookeeper.fullnameOverride=$(NAME)-zookeeper \
		--set externalAccess.service.domain=$(EXTERNAL_IP) \
		--version $(CHART_VERSION) \
		$(HELM_RELEASE) $(CHART_REPO)/$(CHART_NAME)

.PHONY: test
test:
	./test.sh $(NAME)-server-0 $(EXTERNAL_IP):30991

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
