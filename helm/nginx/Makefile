NAME := nginx-proxy
CHART_NAME := bitnami/nginx
CHART_VERSION := 5.1.7

# Default namespace
ifndef NAMESPACE
	NAMESPACE=default
endif


default: status

.PHONY: check
check:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set ingress.enabled=true \
		--set ingress.hosts\[0\].name=$(DOMAIN) \
		--set service.type=ClusterIP \
		--version $(CHART_VERSION) \
		$(NAMESPACE)-$(NAME) $(CHART_NAME)

.PHONY: deploy
deploy:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set ingress.enabled=true \
		--set ingress.hosts\[0\].name=$(DOMAIN) \
		--set service.type=ClusterIP \
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
	helm ls
	helm del --purge $(NAMESPACE)-$(NAME) ||:
