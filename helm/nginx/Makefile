NAME := nginx-proxy
VERSION := 4.3.6

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
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--set ingress.enabled=true \
		--set ingress.hosts\[0\].name=$(DOMAIN) \
		--set service.type=ClusterIP \
		--version $(VERSION) \
		$(NAMESPACE)-$(NAME) bitnami/nginx

.PHONY: install
install:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--set ingress.enabled=true \
		--set ingress.hosts\[0\].name=$(DOMAIN) \
		--set service.type=ClusterIP \
		--version $(VERSION) \
		$(NAMESPACE)-$(NAME) bitnami/nginx

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAMESPACE)-$(NAME)

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAMESPACE)-$(NAME) ||:
