NAME := rabbitmq
CHART_REPO := stable
CHART_NAME := rabbitmq
CHART_VERSION := 6.8.3

# Default namespace
ifndef NAMESPACE
	NAMESPACE=default
endif

# Default local port
ifndef LOCALPORT
	LOCALPORT=
endif

# Ingress controller detection
INGRESS_ENABLED=$(shell kubectl get ClusterRoleBinding 2> /dev/null | grep -q ^ingress && echo true || echo false)

ifeq ($(shell helm version | grep -c v2), 1)
	HELM_DELETE=helm delete -n $(NAMESPACE) $(NAMESPACE)-$(NAME)
	HELM_LIST=helm list -n $(NAMESPACE) --all
	HELM_STATUS=helm status -n $(NAMESPACE) $(NAMESPACE)-$(NAME)
else
	HELM_DELETE=helm delete --purge $(NAMESPACE)-$(NAME)
	HELM_LIST=helm list $(NAMESPACE)-$(NAME)
	HELM_STATUS=helm status $(NAMESPACE)-$(NAME)
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
		--set rabbitmq.username=guest \
		--set rabbitmq.password=guest \
		--set ingress.enabled=$(INGRESS_ENABLED) \
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
		--set rabbitmq.username=guest \
		--set rabbitmq.password=guest \
		--set ingress.enabled=$(INGRESS_ENABLED) \
		--version $(CHART_VERSION) \
		$(NAMESPACE)-$(NAME) $(CHART_REPO)/$(CHART_NAME)

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	@if [ "`helm version | grep v2`" ]; then \
		helm status $(NAMESPACE)-$(NAME); \
		helm ls $(NAMESPACE)-$(NAME); \
	else \
		helm status -n $(NAMESPACE) $(NAMESPACE)-$(NAME); \
		helm list -n $(NAMESPACE) --all; \
	fi

.PHONY: forward
forward:
	kubectl --namespace=$(NAMESPACE) get secret rabbitmq -o jsonpath="{.data.rabbitmq-password}" | \
		base64 -d |  awk '{printf("Username: guest\nPassword: %s\n", $$1)}'
	kubectl --namespace=$(NAMESPACE) port-forward service/$(NAME) $(LOCALPORT):15672

.PHONY: connect
connect:
	./connect.sh

.PHONY: version
version:
	@if [ "`helm version | grep v2`" ]; then \
		helm search -l $(CHART_REPO)/$(CHART_NAME) | tail -n +2 | \
			grep -B 1000 "^$(CHART_REPO)/$(CHART_NAME)[	 ]*$(CHART_VERSION) " | \
			sed -e "s/	/   /g" -e "s/   */   /g"; \
	else \
		helm search repo -l $(CHART_REPO)/$(CHART_NAME) | tail -n +2 | \
			grep -B 1000 "^$(CHART_REPO)/$(CHART_NAME)[	 ]*$(CHART_VERSION) " | \
			sed -e "s/	/   /g" -e "s/   */   /g"; \
	fi

.PHONY: delete
delete:
	$(HELM_LIST)
	$(HELM_DELETE) ||:

.PHONY: clean
clean:
	rm -rf $(CHART_NAME)-*.tgz $(CHART_NAME)
