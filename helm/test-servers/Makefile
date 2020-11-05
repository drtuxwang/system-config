NAME := test-servers
CHART_REPO := .
CHART_NAME := test-servers
IMAGE := drtuxwang/debian-bash:stable
DOMAIN := example.com

# Default namespace
ifndef NAMESPACE
	NAMESPACE=default
endif

# Default local port
ifndef LOCALPORT
	LOCALPORT=
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
		--set ingress.server.domain=$(DOMAIN) \
		$(NAMESPACE)-$(NAME) $(CHART_REPO)/$(CHART_NAME)

.PHONY: template
template:
	helm template --name=$(NAME) \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set image.name=$(IMAGE) \
		--set ingress.server.domain=$(DOMAIN) \
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
		--set ingress.server.domain=$(DOMAIN) \
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
	@if [ "`helm version | grep v2`" ]; then \
		helm ls $(NAMESPACE)-$(NAME); \
		helm del --purge $(NAMESPACE)-$(NAME) ||:; \
	else \
		helm list -n $(NAMESPACE) --all; \
		helm uninstall -n $(NAMESPACE) $(NAMESPACE)-$(NAME) ||:; \
	fi

.PHONY: clean
clean:
