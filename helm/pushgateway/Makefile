NAME := pushgateway
CHART_NAME := stable/prometheus-pushgateway
CHART_VERSION := 1.2.15

# Default namespace
ifndef NAMESPACE
	NAMESPACE=default
endif


default: status

.PHONY: fetch
fetch:
	helm fetch --version=$(CHART_VERSION) $(CHART_NAME)
	rm -rf $(NAME)
	tar xf $(NAME)-$(CHART_VERSION).tgz
	cp -p _helpers.tpl $(NAME)/templates/

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
		$(NAMESPACE)-$(NAME) $(CHART_NAME)

.PHONY: deploy
deploy:
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--version $(CHART_VERSION) \
		$(NAMESPACE)-$(NAME) $(CHART_NAME)

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAMESPACE)-$(NAME)

.PHONY: version
version:
	@helm search -l $(CHART_NAME) | grep "$(CHART_NAME)[	 ]*$(CHART_VERSION) "

.PHONY: clean
clean:
	helm ls $(NAMESPACE)-$(NAME)
	helm del --purge $(NAMESPACE)-$(NAME) ||:
