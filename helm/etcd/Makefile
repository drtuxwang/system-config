NAME := etcd
CHART_REPO := bitnami
CHART_NAME := etcd
CHART_VERSION := 4.11.1

# Default namespace
ifndef NAMESPACE
	NAMESPACE=infra
endif


default: status

.PHONY: repo-add
repo-add:
	helm repo list | grep -q bitnami || helm repo add $(CHART_REPO) https://charts.bitnami.com/bitnami

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

.PHONY: connect
connect:
	@echo "\n*** Connecting to Etcd database ***"
	kubectl -n $(NAMESPACE) exec etcd-0 -- etcdctl -w table member list
	kubectl -n $(NAMESPACE) exec -it etcd-0 -- sh

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
