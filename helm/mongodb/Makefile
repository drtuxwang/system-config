NAME := mongodb
CHART_REPO := bitnami
CHART_NAME := mongodb
CHART_VERSION := 7.14.8

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
	helm status $(NAMESPACE)-$(NAME)

.PHONY: connect
connect:
	@echo "\n*** Connecting to Mongodb database ***"
	@echo "Addresss = `kubectl --namespace=$(NAMESPACE) get service mongodb-server | awk 'NR==2 {print $$3}'`"
	@robo3t

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
