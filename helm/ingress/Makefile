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
	helm repo list | grep -q ingress-nginx || helm repo add $(CHART_REPO) https://kubernetes.github.io/ingress-nginx

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
	@if [ "`helm version | grep v2`" ]; then \
		helm ls $(NAMESPACE)-$(NAME); \
		helm status $(NAMESPACE)-$(NAME); \
	else \
		helm -n $(NAMESPACE) ls; \
		helm -n $(NAMESPACE) status $(NAMESPACE)-$(NAME); \
	fi
	@echo "Example settings for \"/etc/hosts\":"
	@grep -R "[.]kube[.]local" ../* | sed -e "s/local.*/local/" | awk '{printf("'$(EXTERNAL_IP)'  %s\n", $$NF)}'

.PHONY: version
version:
	@helm search -l $(CHART_REPO)/$(CHART_NAME) | tail -n +2 | \
		grep -B 1000 "^$(CHART_REPO)/$(CHART_NAME)[	 ]*$(CHART_VERSION) " | \
		sed -e "s/	/   /g" -e "s/   */   /g"

.PHONY: uninstall
uninstall:
	@if [ "`helm version | grep v2`" ]; then \
		helm ls $(NAMESPACE)-$(NAME); \
		helm del --purge $(NAMESPACE)-$(NAME) ||:; \
	else \
		helm -n $(NAMESPACE) ls -a; \
		helm -n $(NAMESPACE) uninstall $(NAMESPACE)-$(NAME) ||:; \
	fi

.PHONY: clean
clean:
	rm -rf $(CHART_NAME)-*.tgz $(CHART_NAME)
