NAME := etcd-server
VERSION := 4.3.4
NAMESPACE := default

default: status

.PHONY: check
check:
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--version $(VERSION) \
		$(NAME) bitnami/etcd

.PHONY: install
install:
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--version $(VERSION) \
		$(NAME) bitnami/etcd

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAME)

.PHONY: connect
connect:
	@echo "\n*** Connecting to Etcd database ***"
	kubectl exec -it etcd-server-0 sh

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAME) ||:
