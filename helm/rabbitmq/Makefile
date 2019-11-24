NAME := rabbitmq-server
VERSION := 6.7.4

# Default namespace
ifndef NAMESPACE
	NAMESPACE=default
endif


default: status

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
		--version $(VERSION) \
		$(NAMESPACE)-$(NAME) stable/rabbitmq

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
		--version $(VERSION) \
		$(NAMESPACE)-$(NAME) stable/rabbitmq

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
	@helm search -l stable/rabbitmq | grep "stable/rabbitmq[	 ]*$(VERSION) "

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAMESPACE)-$(NAME) ||:
