NAME := servers-test
IMAGE := alpine:3.8

NAMESPACE := servers-test
DOMAIN := example.com

# Default local port
ifndef LOCALPORT
	LOCALPORT=8080
endif

default: status

.PHONY: check
check:
	helm install --name=$(NAME) \
		--namespace=$(NAMESPACE) \
		--set image.server=$(IMAGE) \
		--set ingress.server.domain=$(DOMAIN) \
		. \
		--dry-run \
		--debug

.PHONY: template
template:
	helm template --name=$(CHART_NAME) \
		--set image.server=$(IMAGE) \
		--set ingress.server.domain=$(DOMAIN) \
		.

.PHONY: template



.PHONY: install
install:
	helm install --name=$(CHART_NAME) \
		--namespace=$(NAMESPACE) \
		--set image.server=$(IMAGE) \
		--set ingress.server.domain=$(DOMAIN) \
		.

.PHONY: upgrade
upgrade:
	helm upgrade $(NAME) .
	sleep 2
	kubectl --namespace$(NAMESPACE) get all

.PHONY: forward
forward:
	kubectl --namespace $(NAMESPACE) describe service/$(CHART_NAME)-server
	kubectl --namespace $(NAMESPACE) port-forward service/$(CHART_NAME)-server $(LOCALPORT):80

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
