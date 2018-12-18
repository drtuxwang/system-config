CHART_NAME := servers-test
NAMESPACE := servers-test
IMAGE := centos:7

default: status

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
	@echo
	kubectl --namespace=$(NAMESPACE) get all -o wide
	@echo
	kubectl --namespace=$(NAMESPACE) get secrets -o wide
	@echo
	kubectl --namespace=$(NAMESPACE) get ingress -o wide

.PHONY: clean
clean:
	helm ls
	helm del --purge $(CHART_NAME) ||:
