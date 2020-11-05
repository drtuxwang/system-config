NAME := chartmuseum
CHART_REPO := stable
CHART_NAME := chartmuseum
CHART_VERSION := 2.13.3
INGRESS_HOST := chartmusuem.local
SECRET := chartmusuem-secret-tls

# Default namespace
ifndef NAMESPACE
	NAMESPACE=infra
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
		--set ingress.enabled=true \
		--set ingress.hosts[0].name=$(INGRESS_HOST) \
		--set ingress.hosts[0].tls=true \
		--set ingress.hosts[0].tlsSecret=$(SECRET) \
		--set service.type=ClusterIP \
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
		--set ingress.enabled=true \
		--set ingress.hosts[0].name=$(INGRESS_HOST) \
		--set ingress.hosts[0].tls=true \
		--set ingress.hosts[0].tlsSecret=$(SECRET) \
		--set service.type=ClusterIP \
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
	rm -rf $(CHART_NAME)-*.tgz $(CHART_NAME)
