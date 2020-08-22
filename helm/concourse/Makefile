NAME := concourse
CHART_NAME := concourse/concourse
CHART_VERSION := 11.2.3

# Default namespace
ifndef NAMESPACE
	NAMESPACE=default
endif

# Default local port
ifndef LOCALPORT
	LOCALPORT=
endif


default: status

.PHONY: fetch
fetch:
	helm fetch --version=$(CHART_VERSION) $(CHART_NAME)
	rm -rf $(NAME)
	tar xf $(NAME)-$(CHART_VERSION).tgz

.PHONY: check
check:
	helm repo add concourse https://concourse-charts.storage.googleapis.com
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set postgresql.fullnameOverride=$(NAME)-postgresql \
		--set service.type=ClusterIP \
		--version $(CHART_VERSION) \
		$(NAMESPACE)-$(NAME) $(CHART_NAME)

.PHONY: install
install:
	helm repo add concourse https://concourse-charts.storage.googleapis.com
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set postgresql.fullnameOverride=$(NAME)-postgresql \
		--set service.type=ClusterIP \
		--version $(CHART_VERSION) \
		$(NAMESPACE)-$(NAME) $(CHART_NAME)

.PHONY: forward
forward:
	@echo "Username: test"
	@echo "Password: test"
	kubectl --namespace $(NAMESPACE) port-forward service/$(NAME)-web $(LOCALPORT):8080

.PHONY: connect
connect:
	./connect.sh

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAMESPACE)-$(NAME)

.PHONY: version
version:
	@helm search -l $(CHART_NAME) | grep "$(CHART_NAME)[	 ]*$(CHART_VERSION) " | sed -e "s/	/   /g" -e "s/   */   /g"

.PHONY: delete
delete:
	helm ls $(NAMESPACE)-$(NAME)
	helm del --purge $(NAMESPACE)-$(NAME) ||:
	sleep 2
	kubectl delete namespace $(NAMESPACE)-$(NAME)-main ||:

.PHONY: clean
clean:
	rm -rf $(NAME)-$(CHART_VERSION).tgz $(NAME)
