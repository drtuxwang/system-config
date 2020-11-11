NAME := oracle-xe
CHART_REPO := .
CHART_NAME := oracle-xe
CHART_VERSION=$(shell awk '/version:/{print $$2}' oracle-xe/Chart.yaml)

# Default namespace
ifndef NAMESPACE
	NAMESPACE=infra
endif

# External IP
ifndef EXTERNAL_IP
	EXTERNAL_IP=$(shell ping -c 1 oracle.kube.local | grep "^PING" | sed -e "s/.* (//;s/).*//")
endif
ifndef EXTERNAL_IP
    EXTERNAL_IP=$(shell kubectl get nodes -o wide | awk 'NR==2{print $$6}')
endif

ifeq ($(shell helm version | grep -c v2), 1)
	HELM_LIST=helm list --all $(NAMESPACE)-$(NAME)
	HELM_STATUS=helm status $(NAMESPACE)-$(NAME)
	HELM_UNINSTALL=helm delete --purge $(NAMESPACE)-$(NAME)
	HELM_VERSION=helm search -l $(CHART_REPO)/$(CHART_NAME)
else
	HELM_LIST=helm list -n $(NAMESPACE) --all | grep $(NAMESPACE)-$(NAME)
	HELM_STATUS=helm status -n $(NAMESPACE) $(NAMESPACE)-$(NAME)
	HELM_UNINSTALL=helm uninstall -n $(NAMESPACE) $(NAMESPACE)-$(NAME)
	HELM_VERSION=helm search repo -l $(CHART_REPO)/$(CHART_NAME)
endif

IMAGES_FILE=../helm-images_$(CHART_NAME)-$(CHART_VERSION).tar

default: status


.PHONY: images
images:
	@make template | grep image: | sed -e 's/.* //;s/"//g' | sort | uniq

.PHONY: pull
pull:
	@for IMAGE in `make --no-print-directory images`; do \
		docker pull $$IMAGE; \
	done

.PHONY: save
save:
	../helm-save.sh $(IMAGES_FILE) $(shell make --no-print-directory images)

.PHONY: template
template:
	helm template \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set service.externalIPs='{$(EXTERNAL_IP)}' \
		$(CHART_REPO)/$(CHART_NAME)

.PHONY: check
check:
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set service.externalIPs='{$(EXTERNAL_IP)}' \
		$(NAMESPACE)-$(NAME) $(CHART_REPO)/$(CHART_NAME)

.PHONY: install
install:
	kubectl get namespace $(NAMESPACE) || kubectl create namespace $(NAMESPACE)
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set service.externalIPs='{$(EXTERNAL_IP)}' \
		$(NAMESPACE)-$(NAME) $(CHART_REPO)/$(CHART_NAME)

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	$(HELM_STATUS)
	$(HELM_LIST)

.PHONY: connect
connect:
	@echo "\n*** Connecting to Oracle XE database ***"
	@echo sqlplus system/oracle@oracle.kube.local
	@sqlplus system/oracle@$(EXTERNAL_IP)

.PHONY: version
version:
	@grep "name:" $(CHART_NAME)/Chart.yaml | awk '{printf("./'$(CHART_NAME)'/%s   ", $$2)}'
	@grep "version:" $(CHART_NAME)/Chart.yaml | awk '{printf("%s   ", $$2)}'
	@grep "appVersion:" $(CHART_NAME)/Chart.yaml | awk '{printf("%s   ", $$2)}'
	@grep "description:" $(CHART_NAME)/Chart.yaml | cut -f2- -d" "

.PHONY: uninstall
uninstall:
	$(HELM_LIST)
	$(HELM_UNINSTALL) ||:

.PHONY: clean
clean:
