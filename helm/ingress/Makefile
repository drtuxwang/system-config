NAME := ingress
CHART_REPO := ingress-nginx
CHART_NAME := ingress-nginx
CHART_VERSION :=  2.12.1

# Default namespace
ifndef NAMESPACE
	NAMESPACE=infra
endif

# External IP
ifndef EXTERNAL_IP
    EXTERNAL_IP=$(shell kubectl get nodes -o wide | awk 'NR==2{print $$6}')
endif


default: status

.PHONY: repo-add
repo-add:
	helm repo list | grep -q ingress-nginx || helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx

.PHONY: fetch
fetch: repo-add
	helm fetch --version=$(CHART_VERSION) $(CHART_REPO)/$(CHART_NAME)
	rm -rf $(CHART_NAME)
	tar xf $(CHART_NAME)-$(CHART_VERSION).tgz

.PHONY: check
check: repo-add
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set controller.service.externalIPs='{$(EXTERNAL_IP)}' \
		--version $(CHART_VERSION) \
		$(NAMESPACE)-$(NAME) $(CHART_REPO)/$(CHART_NAME)

.PHONY: install
install: repo-add
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set controller.service.externalIPs='{$(EXTERNAL_IP)}' \
		--version $(CHART_VERSION) \
		$(NAMESPACE)-$(NAME) $(CHART_REPO)/$(CHART_NAME)

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAMESPACE)-$(NAME)
	@echo "Example settings for \"/etc/hosts\":"
	@grep -R "[.]kube[.]local" ../* | sed -e "s/local.*/local/" | awk '{printf("'$(EXTERNAL_IP)'  %s\n", $$NF)}'

.PHONY: version
version:
	@VERSION=`helm search -l $(CHART_REPO)/$(CHART_NAME) | grep "/$(CHART_NAME)[	 ]"`; \
		echo "$$VERSION" | awk 'NR==1 {printf("%s   %s   %s\n", $$1, $$2, $$3)}'; \
		echo "$$VERSION" | grep "[▸  ]*$(CHART_VERSION) " | sed -e "s/▸/   /g" -e "s/   */   /g"

.PHONY: delete
delete:
	helm ls $(NAMESPACE)-$(NAME)
	helm del --purge $(NAMESPACE)-$(NAME) ||:

.PHONY: clean
clean:
	rm -rf $(CHART_NAME)-$(CHART_VERSION).tgz $(CHART_NAME)
