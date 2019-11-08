NAME := oracle-xe
IMAGE := datagrip/oracle:11.2

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
		--set fullnameOverride=$(NAME) \
		--set image.name=$(IMAGE) \
		$(NAMESPACE)-$(NAME) .

.PHONY: template
template:
	helm template --name=$(NAME) \
		--namespace=$(NAMESPACE) \
		--set fullnameOverride=$(NAME) \
		--set image.name=$(IMAGE) \
		.

.PHONY: install
install:
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--set fullnameOverride=$(NAME) \
		--set image.name=$(IMAGE) \
		$(NAMESPACE)-$(NAME) .

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAMESPACE)-$(NAME)

.PHONY: connect
connect:
	@echo "\n*** Connecting to Oracle XE database ***"
	@echo sqlplus system/oracle@`kubectl get service oracle-server-oracle | awk 'NR==2 {print $$3}'`
	@sqlplus system/oracle@`kubectl get service oracle-server-oracle | awk 'NR==2 {print $$3}'`

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAMESPACE)-$(NAME) ||:
