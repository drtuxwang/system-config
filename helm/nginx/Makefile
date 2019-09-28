NAME := nginx-proxy
VERSION := 4.3.6
NAMESPACE := default

default: status

.PHONY: setup_helm
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm repo update

.PHONY: check
check: setup_helm
	helm install -n $(NAME) \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--version $(VERSION) \
		stable/nginx \
		--dry-run \
		--debug

.PHONY: install
install: setup_helm
	helm install -n $(NAME) \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--version $(VERSION) \
		stable/nginx
	sleep 2
	kubectl --namespace=$(NAMESPACE) get all

.PHONY: upgrade
upgrade:
	helm upgrade $(NAME) .

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAME)

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAME) ||:
