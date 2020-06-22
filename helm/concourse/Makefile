NAME := concourse
CHART_NAME := concourse/concourse
CHART_VERSION := 11.2.1

# Default namespace
ifndef NAMESPACE
	NAMESPACE=default
endif

# Default local port
ifndef LOCALPORT
	LOCALPORT=8080
endif


default: status

.PHONY: fetch
fetch:
	helm fetch --version=$(CHART_VERSION) $(CHART_NAME)
	rm -rf $(NAME)
	tar xf $(NAME)-$(CHART_VERSION).tgz
	cp -p _helpers.tpl concourse/templates/

.PHONY: check
check: fetch
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
		$(NAMESPACE)-$(NAME) ./$(NAME)
##		--version $(CHART_VERSION) \
##		$(NAMESPACE)-$(NAME) $(CHART_NAME)

.PHONY: deploy
deploy: fetch
	helm repo add concourse https://concourse-charts.storage.googleapis.com
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set postgresql.fullnameOverride=$(NAME)-postgresql \
		--set service.type=ClusterIP \
		$(NAMESPACE)-$(NAME) ./$(NAME)
##		--version $(CHART_VERSION) \
##		$(NAMESPACE)-$(NAME) $(CHART_NAME)

.PHONY: forward
forward:
##	kubectl --namespace $(NAMESPACE) describe service/$(NAME)-web
##	kubectl --namespace $(NAMESPACE) port-forward service/$(NAME)-web $(LOCALPORT):8080
	kubectl --namespace $(NAMESPACE) describe service/$(NAMESPACE)-$(NAME)-web
	kubectl --namespace $(NAMESPACE) port-forward service/$(NAMESPACE)-$(NAME)-web $(LOCALPORT):8080

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAMESPACE)-$(NAME)

.PHONY: version
version:
	@helm search -l $(CHART_NAME) | grep "$(CHART_NAME)[	 ]*$(CHART_VERSION) "

.PHONY: clean
clean:
	helm ls $(NAMESPACE)-$(NAME)
	helm del --purge $(NAMESPACE)-$(NAME) ||:
	sleep 2
	kubectl delete namespace $(NAMESPACE)-$(NAME)-main ||:

