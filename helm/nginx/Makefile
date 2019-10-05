NAME := nginx-proxy
VERSION := 4.3.6
NAMESPACE := default

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
		--version $(VERSION) \
		$(NAME) bitnami/nginx

# Can't use --wait due to LoadBalancer not assigned external-IP
.PHONY: install
install:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm upgrade \
		--install \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--version $(VERSION) \
		$(NAME) bitnami/nginx

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAME)

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAME) ||:
