NAME := jenkins
CHART_REPO := bitnami
CHART_NAME := jenkins
CHART_VERSION := 5.0.14

# Default namespace
ifndef NAMESPACE
	NAMESPACE=default
endif

# Default local port
ifndef LOCALPORT
	LOCALPORT=
endif


default: status

.PHONY: repo-add
repo-add:
	helm repo add bitnami https://charts.bitnami.com/bitnami

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
		--set service.type=ClusterIP \
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
		--set service.type=ClusterIP \
		--version $(CHART_VERSION) \
		$(NAMESPACE)-$(NAME) $(CHART_REPO)/$(CHART_NAME)

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAMESPACE)-$(NAME)

.PHONY: forward
forward:
	@kubectl --namespace=$(NAMESPACE) get secret $(NAME) -o jsonpath="{.data.jenkins-password}" | \
		base64 -d | awk '{printf("Username: user\nPassword: %s\n", $$1)}'
	kubectl --namespace=$(NAMESPACE) port-forward service/$(NAME) $(LOCALPORT):80

.PHONY: connect
connect:
	./connect.sh

.PHONY: version
version:
	@helm search -l $(CHART_NAME) | grep "$(CHART_NAME)[	 ]*$(CHART_VERSION) " | sed -e "s/	/   /g" -e "s/   */   /g"

.PHONY: delete
delete:
	helm ls $(NAMESPACE)-$(NAME)
	helm del --purge $(NAMESPACE)-$(NAME) ||:

.PHONY: clean
clean:
	rm -rf $(NAME)-$(CHART_VERSION).tgz $(NAME)
