NAME := concourse
CHART_REPO := concourse
CHART_NAME := concourse
CHART_VERSION := 13.0.0

# Default namespace
ifndef NAMESPACE
	NAMESPACE=infra
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


.PHONY: repo-add
repo-add:
	helm repo list | grep -q concourse || helm repo add $(CHART_REPO) https://concourse-charts.storage.googleapis.com

.PHONY: fetch
fetch: repo-add
	helm fetch --version=$(CHART_VERSION) $(CHART_REPO)/$(CHART_NAME)
	rm -rf $(CHART_NAME)
	tar xf $(CHART_NAME)-$(CHART_VERSION).tgz

.PHONY: check
check: repo-add
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set postgresql.fullnameOverride=$(NAME)-postgresql \
		--set service.type=ClusterIP \
		--set web.ingress.enabled=$(INGRESS_ENABLED) \
		--version $(CHART_VERSION) \
		$(NAMESPACE)-$(NAME) $(CHART_REPO)/$(CHART_NAME)

.PHONY: install
install: repo-add fetch
	cp -p  web-ingress.yaml  concourse/templates/
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set postgresql.fullnameOverride=$(NAME)-postgresql \
		--set service.type=ClusterIP \
		--set web.ingress.enabled=$(INGRESS_ENABLED) \
		--version $(CHART_VERSION) \
		$(NAMESPACE)-$(NAME) ./$(CHART_NAME)
##		$(NAMESPACE)-$(NAME) $(CHART_REPO)/$(CHART_NAME)

.PHONY: forward
forward:
	@echo "Username: test"
	@echo "Password: test"
	kubectl --namespace=$(NAMESPACE) port-forward service/$(NAME)-web $(LOCALPORT):8080

.PHONY: connect
connect:
	./connect.sh

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
	sleep 2
	kubectl delete namespace $(NAMESPACE)-$(NAME)-main ||:

.PHONY: clean
clean:
	rm -rf $(CHART_NAME)-*.tgz $(CHART_NAME)
