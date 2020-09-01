#
# Requires "$EXTERNAL_IP  host.kube.local" entries in DNS or /etc/hosts
#
NAME := ingress
CHART_REPO := ingress-nginx
CHART_NAME := ingress-nginx
CHART_VERSION :=  2.12.1

# Default namespace
ifndef NAMESPACE
	NAMESPACE=default
endif

# External IP
ifndef EXTERNAL_IP
    EXTERNAL_IP=$(shell kubectl get nodes -o wide | awk 'NR==2{print $$6}')
endif

# Default local port
ifndef LOCALPORT
	LOCALPORT=8080
endif
ifndef LOCALPORT_HTTPS
	LOCALPORT_HTTPS=8443
endif


default: status

.PHONY: repo-add
repo-add:
	helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx

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

.PHONY: forward
forward:
	kubectl --namespace=$(NAMESPACE) port-forward service/$(NAME)-controller $(LOCALPORT):80 $(LOCALPORT_HTTPS):443

.PHONY: version
version:
	@helm search -l $(CHART_NAME) | grep "$(CHART_NAME)[	 ]*$(CHART_VERSION) " | sed -e "s/	/   /g" -e "s/   */   /g"

.PHONY: delete
delete:
	helm ls $(NAMESPACE)-$(NAME)
	helm del --purge $(NAMESPACE)-$(NAME) ||:

.PHONY: clean
clean:
	rm -rf $(CHART_NAME)-$(CHART_VERSION).tgz $(CHART_NAME)
