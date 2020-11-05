NAME := mongodb
CHART_REPO := bitnami
CHART_NAME := mongodb
CHART_VERSION := 8.3.2

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
	@if [ "`helm version | grep v2`" ]; then \
		helm ls $(NAMESPACE)-$(NAME); \
		helm status $(NAMESPACE)-$(NAME); \
	else \
		helm -n $(NAMESPACE) ls; \
		helm -n $(NAMESPACE) status $(NAMESPACE)-$(NAME); \
	fi

.PHONY: connect
connect:
	@echo "\n*** Connecting to Mongodb database ***"
	@echo "Addresss = `kubectl --namespace=$(NAMESPACE) get service mongodb-server | awk 'NR==2 {print $$3}'`"
	@robo3t

.PHONY: version
version:
	@helm search -l $(CHART_REPO)/$(CHART_NAME) | tail -n +2 | \
		grep -B 1000 "^$(CHART_REPO)/$(CHART_NAME)[	 ]*$(CHART_VERSION) " | \
		sed -e "s/	/   /g" -e "s/   */   /g"

.PHONY: uninstall
uninstall:
	@if [ "`helm version | grep v2`" ]; then \
		helm ls $(NAMESPACE)-$(NAME); \
		helm del --purge $(NAMESPACE)-$(NAME) ||:; \
	else \
		helm -n $(NAMESPACE) ls -a; \
		helm -n $(NAMESPACE) uninstall $(NAMESPACE)-$(NAME) ||:; \
	fi

.PHONY: clean
clean:
	rm -rf $(CHART_NAME)-*.tgz $(CHART_NAME)
