NAME := rabbitmq
CHART_NAME := stable/rabbitmq
CHART_VERSION := 6.8.3

# Default namespace
ifndef NAMESPACE
	NAMESPACE=default
endif


default: status

.PHONY: fetch
fetch:
	helm fetch --version=$(CHART_VERSION) $(CHART_NAME)
	rm -rf $(NAME)
	tar xf $(NAME)-$(CHART_VERSION).tgz

.PHONY: check
check:
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set rabbitmq.username=guest \
		--set rabbitmq.password=guest \
		--version $(CHART_VERSION) \
		$(NAMESPACE)-$(NAME) $(CHART_NAME)

.PHONY: deploy
deploy:
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set rabbitmq.username=guest \
		--set rabbitmq.password=guest \
   	--version $(CHART_VERSION) \
		$(NAMESPACE)-$(NAME) $(CHART_NAME)

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAMESPACE)-$(NAME)

.PHONY: connect
connect:
	@echo "\n*** Connecting to RabbitMQ server ***"
	@echo "firefox http://`kubectl get service rabbitmq-server | awk 'NR==2 {print $$3}'`:15672"
	@firefox http://`kubectl get service rabbitmq-server | awk 'NR==2 {print $$3}'`:15672

.PHONY: version
version:
	@helm search -l $(CHART_NAME) | grep "$(CHART_NAME)[	 ]*$(CHART_VERSION) "

.PHONY: clean
clean:
	helm ls $(NAMESPACE)-$(NAME)
	helm del --purge $(NAMESPACE)-$(NAME) ||:
