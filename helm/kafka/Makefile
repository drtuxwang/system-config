NAME := kafka-server
VERSION := 0.18.2

# Default namespace
ifndef NAMESPACE
	NAMESPACE=default
endif


default: status

.PHONY: check
check:
	helm repo add incubator https://kubernetes-charts-incubator.storage.googleapis.com
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		--namespace=$(NAMESPACE) \
		--set fullnameOverride=$(NAME) \
		--set zookeeper.fullnameOverride=$(NAME)-zookeeper \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--set persistence.enabled=false \
		--version $(VERSION) \
		$(NAMESPACE)-$(NAME) incubator/kafka

.PHONY: deploy
deploy:
	helm repo add incubator https://kubernetes-charts-incubator.storage.googleapis.com
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--set fullnameOverride=$(NAME) \
		--set zookeeper.fullnameOverride=$(NAME)-zookeeper \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--set persistence.enabled=false \
		--version $(VERSION) \
		$(NAMESPACE)-$(NAME) incubator/kafka

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAMESPACE)-$(NAME)

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAMESPACE)-$(NAME) ||:
