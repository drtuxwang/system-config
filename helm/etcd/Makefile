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
	helm status $(NAMESPACE)-$(NAME)

.PHONY: connect
connect:
	@echo "\n*** Connecting to Etcd database ***"
	kubectl -n $(NAMESPACE) exec etcd-0 -- etcdctl -w table member list
	kubectl -n $(NAMESPACE) exec -it etcd-0 -- sh

.PHONY: version
version:
	@VERSION=`helm search -l $(CHART_REPO)/$(CHART_NAME) | grep "/$(CHART_NAME)[	 ]"`; \
		echo "$$VERSION" | awk 'NR==1 {printf("%s   %s   %s\n", $$1, $$2, $$3)}'; \
		echo "$$VERSION" | grep "[▸  ]*$(CHART_VERSION) " | sed -e "s/	/   /g" -e "s/   */   /g"

.PHONY: delete
delete:
	helm ls $(NAMESPACE)-$(NAME)
	helm del --purge $(NAMESPACE)-$(NAME) ||:

.PHONY: clean
clean:
	rm -rf $(CHART_NAME)-$(CHART_VERSION).tgz $(CHART_NAME)
