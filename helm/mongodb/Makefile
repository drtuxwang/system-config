NAME := mongodb-server
VERSION := 6.1.5
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
		$(NAME) stable/mongodb

.PHONY: install
install:
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--version $(VERSION) \
		$(NAME) stable/mongodb

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAME)

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAME) ||:
