NAME := concourse-server
VERSION := 8.2.3

# Default namespace
ifndef NAMESPACE
	NAMESPACE=default
endif

# Default local port
ifndef LOCALPORT
	LOCALPORT=8080
endif


default: status

.PHONY: check
check:
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		--namespace=$(NAMESPACE) \
		--set fullnameOverride=$(NAME) \
		--set persistence.enabled=false \
		--set postgresql.persistence.enabled=false \
		--set service.type=ClusterIP \
		--version $(VERSION) \
		$(NAMESPACE)-$(NAME) stable/concourse

.PHONY: install
install:
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--set fullnameOverride=$(NAME) \
		--set persistence.enabled=false \
		--set postgresql.persistence.enabled=false \
		--set service.type=ClusterIP \
		--version $(VERSION) \
		$(NAMESPACE)-$(NAME) stable/concourse

.PHONY: forward
forward:
	kubectl --namespace $(NAMESPACE) port-forward service/concourse-web $(LOCALPORT):8080

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAMESPACE)-$(NAME)

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAMESPACE)-$(NAME) ||:
	sleep 2
	kubectl delete namespace $(NAME)-main ||:

