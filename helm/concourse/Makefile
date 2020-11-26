NAME := concourse
CHART_REPO := concourse
CHART_URL := https://concourse-charts.storage.googleapis.com
CHART_NAME := concourse
CHART_VERSION := 14.3.1
APP_VERSION=$(shell make --no-print-directory version | awk 'END {print $$3}')

# Default namespace
ifndef NAMESPACE
	NAMESPACE=infra
endif

# Default local port
ifndef LOCALPORT
	LOCALPORT=
endif

# Ingress controller detection
ifndef INGRESS_ENABLED
	INGRESS_ENABLED=$(shell kubectl get ClusterRoleBinding 2> /dev/null | grep -q ^ingress && echo true || echo false)
endif

ifeq ($(shell helm version | grep -c v2), 1)
	HELM_RELEASE=$(NAMESPACE)-$(NAME)
	HELM_LIST=helm list --all $(HELM_RELEASE)
	HELM_STATUS=helm status $(HELM_RELEASE)
	HELM_UNINSTALL=helm delete --purge $(HELM_RELEASE)
	HELM_VERSION=helm search -l $(CHART_REPO)/$(CHART_NAME)
else
	HELM_RELEASE=$(NAME)
	HELM_LIST=helm --namespace=$(NAMESPACE) list --all | grep $(HELM_RELEASE)
	HELM_STATUS=helm --namespace=$(NAMESPACE) status $(HELM_RELEASE)
	HELM_UNINSTALL=helm --namespace=$(NAMESPACE) uninstall $(HELM_RELEASE)
	HELM_VERSION=helm search repo -l $(CHART_REPO)/$(CHART_NAME)
endif

IMAGES_FILE=../$(CHART_REPO)-$(CHART_NAME)-$(CHART_VERSION)_app-$(APP_VERSION)_images.tar

default: status


.PHONY: repo-add
repo-add:
	helm repo list | grep -q $(CHART_REPO) || helm repo add $(CHART_REPO) $(CHART_URL)

.PHONY: fetch
fetch: repo-add clean
	mkdir $(CHART_REPO) && \
		cd $(CHART_REPO) && \
		helm fetch --untar --version=$(CHART_VERSION) $(CHART_REPO)/$(CHART_NAME)

.PHONY: images
images:
	@INGRESS_ENABLED=false make template | grep image: | sed -e 's/.* //;s/"//g' | sort | uniq

.PHONY: pull
pull:
	@for IMAGE in `make --no-print-directory images`; do \
		docker pull $$IMAGE; \
	done

.PHONY: save
save:
	../helm-save.sh $(IMAGES_FILE) $(shell make --no-print-directory images)

.PHONY: template
template: repo-add
	helm template \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set postgresql.fullnameOverride=$(NAME)-postgresql \
		--set service.type=ClusterIP \
		--set web.ingress.enabled=$(INGRESS_ENABLED) \
		--version $(CHART_VERSION) \
		$(CHART_REPO)/$(CHART_NAME)

.PHONY: check
check: repo-add
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set postgresql.fullnameOverride=$(NAME)-postgresql \
		--set service.type=ClusterIP \
		--set web.ingress.enabled=$(INGRESS_ENABLED) \
		--version $(CHART_VERSION) \
		$(HELM_RELEASE) $(CHART_REPO)/$(CHART_NAME)

.PHONY: install
install: repo-add
	kubectl get namespace $(NAMESPACE) || kubectl create namespace $(NAMESPACE)
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set postgresql.fullnameOverride=$(NAME)-postgresql \
		--set service.type=ClusterIP \
		--set web.ingress.enabled=$(INGRESS_ENABLED) \
		--version $(CHART_VERSION) \
		$(HELM_RELEASE) $(CHART_REPO)/$(CHART_NAME)

.PHONY: forward
forward:
	@echo "Username: test"
	@echo "Password: test"
	kubectl --namespace=$(NAMESPACE) port-forward service/$(NAME)-web $(LOCALPORT):8080

.PHONY: connect
connect:
	./connect.sh

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	$(HELM_STATUS)
	$(HELM_LIST)

.PHONY: version
version:
	@$(HELM_VERSION) | tail -n +2 | \
		grep -B 1000 "^$(CHART_REPO)/$(CHART_NAME)[	 ]*$(CHART_VERSION) " | \
		sed -e "s/	/   /g" -e "s/   */   /g"

.PHONY: uninstall
uninstall:
	$(HELM_LIST)
	$(HELM_UNINSTALL) ||:
	sleep 2
	kubectl delete namespace $(NAME)-main ||:

.PHONY: clean
clean:
	rm -rf $(CHART_REPO)
