NAME := nexus-server
VERSION := 1.18.5
NAMESPACE := default

default: status

.PHONY: check
check:
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		--namespace=$(NAMESPACE) \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--set persistence.enabled=false \
		--version $(VERSION) \
		$(NAME) stable/sonatype-nexus

.PHONY: install
install:
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--set persistence.enabled=false \
		--version $(VERSION) \
		$(NAME) stable/sonatype-nexus

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAME)

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAME) ||: