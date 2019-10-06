NAME := servers-test
IMAGE := alpine:3.9
NAMESPACE := servers-test
DOMAIN := example.com

# Default local port
ifndef LOCALPORT
	LOCALPORT=8080
endif

default: status

.PHONY: check
check:
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		--namespace=$(NAMESPACE) \
		--set image.server=$(IMAGE) \
		--set ingress.server.domain=$(DOMAIN) \
		$(NAME) .

.PHONY: template
template:
	helm template --name=$(NAME) \
		--set image.server=$(IMAGE) \
		--set ingress.server.domain=$(DOMAIN) \
		.

.PHONY: install
install:
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--set image.server=$(IMAGE) \
		--set ingress.server.domain=$(DOMAIN) \
		$(NAME) .

.PHONY: forward
forward:
	kubectl --namespace $(NAMESPACE) describe service/$(NAME)-server
	kubectl --namespace $(NAMESPACE) port-forward service/$(NAME)-server $(LOCALPORT):80

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAME)

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAME) ||:
	sleep 4
	kubectl delete namespace servers-test
