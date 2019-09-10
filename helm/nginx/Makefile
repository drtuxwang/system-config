NAME := nginx-proxy
NAMESPACE := default

default: status

.PHONY: check
check:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm install -n $(NAME) \
		--namespace=$(NAMESPACE) \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--version 4.3.3 \
		bitnami/nginx \
		--dry-run \
		--debug

.PHONY: install
install:
	helm repo add stable https://kubernetes-charts.storage.googleapis.com
	helm install -n $(NAME) \
		--namespace=$(NAMESPACE) \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--version 4.3.3 \
		bitnami/nginx \
	sleep 2
	kubectl --namespace=$(NAMESPACE) get all

.PHONY: upgrade
upgrade:
	helm upgrade $(NAME) .

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm ls
	@echo
	kubectl --namespace=$(NAMESPACE) get all -o wide

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAME) ||:
