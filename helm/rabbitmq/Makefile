NAME := rabbitmq-server
VERSION := 6.7.4
NAMESPACE := default

default: status

.PHONY: check
check:
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		--namespace=$(NAMESPACE) \
		--set persistence.enabled=false \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--version $(VERSION) \
		$(NAME) stable/rabbitmq

.PHONY: install
install:
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--set persistence.enabled=false \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--set rabbitmq.username=guest \
		--set rabbitmq.password=guest \
		--version $(VERSION) \
		$(NAME) stable/rabbitmq

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAME)

.PHONY: connect
connect:
	@echo "\n*** Connecting to RabbitMQ server ***"
	@echo "firefox http://`kubectl get service rabbitmq-server | awk 'NR==2 {print $$3}'`:15672"
	@firefox http://`kubectl get service rabbitmq-server | awk 'NR==2 {print $$3}'`:15672

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAME) ||:
