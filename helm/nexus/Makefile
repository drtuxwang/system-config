NAME := nexus-server
VERSION := 1.18.5

# Default namespace
ifndef NAMESPACE
	NAMESPACE=default
endif

default: status

.PHONY: check
check:
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--version $(VERSION) \
		$(NAMESPACE)-$(NAME) stable/sonatype-nexus

.PHONY: deploy
deploy:
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--version $(VERSION) \
		$(NAMESPACE)-$(NAME) stable/sonatype-nexus

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAMESPACE)-$(NAME)

.PHONY: version
version:
	@helm search -l stable/sonatype-nexus | grep "stable/sonatype-nexus[	 ]$(VERSION) "

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAMESPACE)-$(NAME) ||:
