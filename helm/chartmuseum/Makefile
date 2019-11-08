NAME := chartmuseum-server
VERSION := 2.3.2
INGRESS_HOST := chartmusuem.local
SECRET := chartmusuem-secret-tls

# Default namespace
ifndef NAMESPACE
	NAMESPACE=default
endif


default: status

.PHONY: check
check:
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		--namespace=$(NAMESPACE) \
		--set fullnameOverride=$(NAME) \
		--set persistence.enabled=false \
		--set env.open.DISABLE_API=false \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--set persistence.enabled=false \
		--set ingress.enabled=true \
		--set ingress.hosts[0].name=$(INGRESS_HOST) \
		--set ingress.hosts[0].tls=true \
		--set ingress.hosts[0].tlsSecret=$(SECRET) \
		--set service.type=ClusterIP \
		--version $(VERSION) \
		$(NAMESPACE)-$(NAME) stable/chartmuseum

.PHONY: deploy
deploy:
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--set fullnameOverride=$(NAME) \
		--set persistence.enabled=false \
		--set env.open.DISABLE_API=false \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--set persistence.enabled=false \
		--set ingress.enabled=true \
		--set ingress.hosts[0].name=$(INGRESS_HOST) \
		--set ingress.hosts[0].tls=true \
		--set ingress.hosts[0].tlsSecret=$(SECRET) \
		--set service.type=ClusterIP \
		--version $(VERSION) \
		$(NAMESPACE)-$(NAME) stable/chartmuseum

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAMESPACE)-$(NAME)

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAMESPACE)-$(NAME) ||:
