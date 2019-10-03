NAME := mongodb-server
VERSION := 6.1.5
NAMESPACE := default

default: status

.PHONY: check
check:
	helm upgrade \
		--install \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--version $(VERSION) \
		$(NAME) stable/mongodb \
		--dry-run \
		--debug

.PHONY: install
install:
	helm upgrade \
		--install \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--version $(VERSION) \
		$(NAME) stable/mongodb
	sleep 2
	kubectl --namespace=$(NAMESPACE) get all

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAME)

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAME) ||:
