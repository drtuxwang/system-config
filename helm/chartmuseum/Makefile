NAME := chartmuseum-server
VERSION := 2.3.2
NAMESPACE := default
INGRESS_HOST := chartmusuem.local
SECRET := chartmusuem-secret-tls


default: status

.PHONY: check
check:
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		--namespace=$(NAMESPACE) \
		--set persistence.enabled=false \
		--set env.open.DISABLE_API=false \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--set persistence.enabled=true \
		--set ingress.enabled=true \
		--set ingress.hosts[0].name=$(INGRESS_HOST) \
		--set ingress.hosts[0].tls=true \
		--set ingress.hosts[0].tlsSecret=$(SECRET) \
		--version $(VERSION) \
		$(NAME) stable/chartmuseum

.PHONY: install
install:
	# Can't use --wait due to external IP pending
	helm upgrade \
		--install \
		--namespace=$(NAMESPACE) \
		--set persistence.enabled=false \
		--set env.open.DISABLE_API=false \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--set persistence.enabled=true \
		--set ingress.enabled=true \
		--set ingress.hosts[0].name=$(INGRESS_HOST) \
		--set ingress.hosts[0].tls=true \
		--set ingress.hosts[0].tlsSecret=$(SECRET) \
		--version $(VERSION) \
		$(NAME) stable/chartmuseum

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAME)

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAME) ||:
