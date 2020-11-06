NAME := pushgateway
CHART_REPO := prometheus-community
CHART_NAME := prometheus-pushgateway
CHART_VERSION := 1.4.2

# Default namespace
ifndef NAMESPACE
	NAMESPACE=infra
endif

ifeq ($(shell helm version | grep -c v3), 1)
	HELM_DELETE=helm -n $(NAMESPACE) delete $(NAMESPACE)-$(NAME)
	HELM_LIST=helm -n $(NAMESPACE) list --all
	HELM_STATUS=helm -n $(NAMESPACE) status $(NAMESPACE)-$(NAME)
	HELM_VERSION=helm search repo -l $(CHART_REPO)/$(CHART_NAME)
else
	HELM_DELETE=helm delete --purge $(NAMESPACE)-$(NAME)
	HELM_LIST=helm list --all $(NAMESPACE)-$(NAME)
	HELM_STATUS=helm status $(NAMESPACE)-$(NAME)
	HELM_VERSION=helm search -l $(CHART_REPO)/$(CHART_NAME) 
endif

default: status


.PHONY: fetch
fetch:
	helm fetch --version=$(CHART_VERSION) $(CHART_REPO)/$(CHART_NAME)
	rm -rf $(CHART_NAME)
	tar xf $(CHART_NAME)-$(CHART_VERSION).tgz

.PHONY: check
check:
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--version $(CHART_VERSION) \
		$(NAMESPACE)-$(NAME) $(CHART_REPO)/$(CHART_NAME)

.PHONY: install
install:
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--version $(CHART_VERSION) \
		$(NAMESPACE)-$(NAME) $(CHART_REPO)/$(CHART_NAME)

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

.PHONY: delete
delete:
	$(HELM_LIST)
	$(HELM_DELETE) ||:

.PHONY: clean
clean:
	rm -rf $(CHART_NAME)-*.tgz $(CHART_NAME)
