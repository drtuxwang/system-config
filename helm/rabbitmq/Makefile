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
	helm status $(NAMESPACE)-$(NAME)

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
	@VERSION=`helm search -l $(CHART_REPO)/$(CHART_NAME) | grep "/$(CHART_NAME)[	 ]"`; \
		echo "$$VERSION" | awk 'NR==1 {printf("%s   %s   %s\n", $$1, $$2, $$3)}'; \
		echo "$$VERSION" | grep "[▸  ]*$(CHART_VERSION) " | sed -e "s/	/   /g" -e "s/   */   /g"

.PHONY: delete
delete:
	helm ls $(NAMESPACE)-$(NAME)
	helm del --purge $(NAMESPACE)-$(NAME) ||:

.PHONY: clean
clean:
	rm -rf $(CHART_NAME)-$(CHART_VERSION).tgz $(CHART_NAME)
