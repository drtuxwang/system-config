NAME := test-server
CHART_REPO := ./drtuxwang
CHART_NAME := test-server
DOMAIN := example.com

# Default namespace
ifndef NAMESPACE
	NAMESPACE=default
endif

# Default local port
ifndef LOCALPORT
	LOCALPORT=
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
		--set ingress.server.domain=$(DOMAIN) \
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
		--set ingress.server.domain=$(DOMAIN) \
		$(HELM_RELEASE) $(CHART_REPO)/$(CHART_NAME)

.PHONY: install
install:
	kubectl get namespace $(NAMESPACE) || kubectl create namespace $(NAMESPACE)
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set ingress.server.domain=$(DOMAIN) \
		$(HELM_RELEASE) $(CHART_REPO)/$(CHART_NAME)

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

.PHONY: forward
forward:
	kubectl --namespace=$(NAMESPACE) port-forward service/$(NAME)-server $(LOCALPORT):80

.PHONY: connect
connect:
	./connect.sh

.PHONY: uninstall
uninstall:
	$(HELM_LIST)
	$(HELM_UNINSTALL) ||:

.PHONY: clean
clean:
