NAME := kafka
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
		--values values.yaml \
		--set fullnameOverride=$(NAME)-server \
		--set zookeeper.fullnameOverride=$(NAME)-zookeeper \
		--version $(VERSION) \
		$(NAMESPACE)-$(NAME) incubator/kafka

.PHONY: deploy
deploy:
	helm repo add incubator https://kubernetes-charts-incubator.storage.googleapis.com
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME)-server \
		--set zookeeper.fullnameOverride=$(NAME)-zookeeper \
		--version $(VERSION) \
		$(NAMESPACE)-$(NAME) incubator/kafka

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAMESPACE)-$(NAME)

.PHONY: version
version:
	@helm search -l incubator/kafka | grep "incubator/kafka[	 ]*$(VERSION) "

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAMESPACE)-$(NAME) ||:
