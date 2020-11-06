NAME := ops-box
CHART_REPO := .
CHART_NAME := ops-box
IMAGE := drtuxwang/debian-bash:stable

# Default namespace
ifndef NAMESPACE
	NAMESPACE=default
endif

ifeq ($(shell helm version | grep -c v3), 1)
	HELM_DELETE=helm -n $(NAMESPACE) delete $(NAMESPACE)-$(NAME)
	HELM_LIST=helm -n $(NAMESPACE) list --all
	HELM_STATUS=helm -n $(NAMESPACE) status $(NAMESPACE)-$(NAME)
else
	HELM_DELETE=helm delete --purge $(NAMESPACE)-$(NAME)
	HELM_LIST=helm list --all $(NAMESPACE)-$(NAME)
	HELM_STATUS=helm status $(NAMESPACE)-$(NAME)
endif

default: status


.PHONY: check
check:
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set image.name=$(IMAGE) \
		--set image.pullPolicy=Always \
		$(NAMESPACE)-$(NAME) $(CHART_REPO)/$(CHART_NAME)

.PHONY: template
template:
	helm template --name=$(NAME) \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set image.name=$(IMAGE) \
		--set image.pullPolicy=Always \
		$(CHART_REPO)/$(CHART_NAME)

.PHONY: install
install:
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set image.name=$(IMAGE) \
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

.PHONY: delete
delete:
	$(HELM_LIST)
	$(HELM_DELETE) ||:

.PHONY: clean
clean:
