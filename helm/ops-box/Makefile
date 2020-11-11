NAME := ops-box
CHART_REPO := .
CHART_NAME := ops-box

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
	HELM_LIST=helm -n $(NAMESPACE) list --all
	HELM_STATUS=helm -n $(NAMESPACE) status $(NAMESPACE)-$(NAME)
	HELM_UNINSTALL=helm -n $(NAMESPACE) uninstall $(NAMESPACE)-$(NAME)
	HELM_VERSION=helm search repo -l $(CHART_REPO)/$(CHART_NAME)
endif

default: status


.PHONY: images
images:
	@make template | grep image: | sed -e 's/.* //;s/"//g' | sort | uniq

.PHONY: pull
pull:

.PHONY: save
save:

.PHONY: template
template:
	helm template \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set image.pullPolicy=Always \
		$(CHART_REPO)/$(CHART_NAME)

.PHONY: check
check:
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set image.pullPolicy=Always \
		$(NAMESPACE)-$(NAME) $(CHART_REPO)/$(CHART_NAME)

.PHONY: install
install:
	kubectl get namespace $(NAMESPACE) || kubectl create namespace $(NAMESPACE)
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set image.pullPolicy=Always \
		$(NAMESPACE)-$(NAME) $(CHART_REPO)/$(CHART_NAME)

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	$(HELM_STATUS)
	$(HELM_LIST)

.PHONY: version
version:
	@grep "name:" $(CHART_NAME)/Chart.yaml | awk '{printf("./'$(CHART_NAME)'/%s   ", $$2)}'
	@grep "version:" $(CHART_NAME)/Chart.yaml | awk '{printf("%s   ", $$2)}'
	@grep "appVersion:" $(CHART_NAME)/Chart.yaml | awk '{printf("%s   ", $$2)}'
	@grep "description:" $(CHART_NAME)/Chart.yaml | cut -f2- -d" "

.PHONY: uninstall
uninstall:
	$(HELM_LIST)
	$(HELM_UNINSTALL) ||:

.PHONY: clean
clean:
