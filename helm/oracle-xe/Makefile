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
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set image.name=$(IMAGE) \
		$(NAMESPACE)-$(NAME) ./helm/oracle-xe

.PHONY: template
template:
	helm template --name=$(NAME) \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set image.name=$(IMAGE) \
		./helm/oracle-xe

.PHONY: deploy
deploy:
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set image.name=$(IMAGE) \
		$(NAMESPACE)-$(NAME) ./helm/oracle-xe

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAMESPACE)-$(NAME)

.PHONY: connect
connect:
	@echo "\n*** Connecting to Oracle XE database ***"
	@echo sqlplus system/oracle@`kubectl get service oracle-server-oracle | awk 'NR==2 {print $$3}'`
	@sqlplus system/oracle@`kubectl get service oracle-server-oracle | awk 'NR==2 {print $$3}'`

.PHONY: version
version:
	@echo "`egrep "name|version:" Chart.yaml | awk '{printf("%s 	 ", $$2)}'` 	 $(IMAGE)"


.PHONY: clean
clean:
	helm ls $(NAMESPACE)-$(NAME)
	helm del --purge $(NAMESPACE)-$(NAME) ||:
