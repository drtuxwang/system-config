CHART_NAME := servers-test
NAMESPACE := default
IMAGE := ubuntu:18.04

default: check

.PHONY: check
check:
	helm install -n $(CHART_NAME) \
		--namespace=$(NAMESPACE) \
		--set image.server=$(IMAGE) \
		. \
		--dry-run \
		--debug

.PHONY: install
install:
	helm install -n $(CHART_NAME) \
		--namespace=$(NAMESPACE) \
		--set image.server=$(IMAGE) \
		.
	sleep 2
	kubectl --namespace=$(NAMESPACE) get all

.PHONY: upgrade
upgrade:
	helm upgrade $(NAME) .
	sleep 2
	kubectl --namespace$(NAMESPACE) get all

.PHONY: forward
forward:
	kubectl --namespace $(NAMESPACE) describe service/$(NAME)-server
	kubectl --namespace $(NAMESPACE) port-forward service/$(NAME)-server 8080:80

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm ls
	kubectl --namespace=$(NAMESPACE) get all

.PHONY: clean
clean:
	helm ls
	helm del --purge $(CHART_NAME) ||:
