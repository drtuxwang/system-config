NAME := nexus-server
VERSION := 1.18.5
NAMESPACE := default

default: status

.PHONY: check
check:
	helm upgrade \
		--install \
		--namespace=$(NAMESPACE) \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--version $(VERSION) \
		$(NAME) --wait stable/sonatype-nexus \
		--dry-run \
		--debug

.PHONY: install
install:
	helm upgrade \
		--install \
		--namespace=$(NAMESPACE) \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--version $(VERSION) \
		$(NAME) --wait stable/sonatype-nexus

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAME)

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAME) ||:
