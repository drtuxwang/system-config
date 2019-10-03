NAME := nginx-proxy
VERSION := 4.3.6
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
		$(NMAE) --wait stable/nginx \
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
		$(NMAE) --wait stable/nginx

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAME)

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAME) ||:
