NAME := etcd-server
VERSION := 4.3.4

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
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--version $(VERSION) \
		$(NAMESPACE)-$(NAME) bitnami/etcd

.PHONY: deploy
deploy:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--version $(VERSION) \
		$(NAMESPACE)-$(NAME) bitnami/etcd

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAMESPACE)-$(NAME)

.PHONY: connect
connect:
	@echo "\n*** Connecting to Etcd database ***"
	kubectl exec -it etcd-server-0 sh

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAMESPACE)-$(NAME) ||:
