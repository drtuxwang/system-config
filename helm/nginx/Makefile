NAME := nginx
CHART_REPO := bitnami
CHART_NAME := nginx
CHART_VERSION := 5.1.12

# Default namespace
ifndef NAMESPACE
	NAMESPACE=default
endif

ifeq ($(shell helm version | grep -c v2), 1)
	HELM_LIST=helm list --all $(NAMESPACE)-$(NAME)
	HELM_STATUS=helm status $(NAMESPACE)-$(NAME)
	HELM_UNINSTALL=helm delete --purge $(NAMESPACE)-$(NAME)
	HELM_VERSION=helm search -l $(CHART_REPO)/$(CHART_NAME)
else
	HELM_LIST=helm list -n $(NAMESPACE) --all | grep $(NAMESPACE)-$(NAME)
	HELM_STATUS=helm status -n $(NAMESPACE) $(NAMESPACE)-$(NAME)
	HELM_UNINSTALL=helm uninstall -n $(NAMESPACE) $(NAMESPACE)-$(NAME)
	HELM_VERSION=helm search repo -l $(CHART_REPO)/$(CHART_NAME)
endif

IMAGES_FILE=../helm-images_$(CHART_NAME)-$(CHART_VERSION).tar

default: status


.PHONY: repo-add
repo-add:
	helm repo list | grep -q bitnami || helm repo add $(CHART_REPO) https://charts.bitnami.com/bitnami

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
	../helm-save.sh $(IMAGES_FILE) $(shell make --no-print-directory images)

.PHONY: template
template: repo-add
	helm template \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set ingress.enabled=true \
		--set ingress.hosts\[0\].name=$(DOMAIN) \
		--set service.type=ClusterIP \
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
		--set fullnameOverride=$(NAME) \
		--set ingress.enabled=true \
		--set ingress.hosts\[0\].name=$(DOMAIN) \
		--set service.type=ClusterIP \
		--version $(CHART_VERSION) \
		$(NAMESPACE)-$(NAME) $(CHART_REPO)/$(CHART_NAME)

.PHONY: install
install: repo-add
	kubectl get namespace $(NAMESPACE) || kubectl create namespace $(NAMESPACE)
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set ingress.enabled=true \
		--set ingress.hosts\[0\].name=$(DOMAIN) \
		--set service.type=ClusterIP \
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

.PHONY: uninstall
uninstall:
	$(HELM_LIST)
	$(HELM_UNINSTALL) ||:

.PHONY: clean
clean:
	rm -rf $(CHART_NAME)-*.tgz $(CHART_NAME)
