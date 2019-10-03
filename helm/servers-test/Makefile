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
	helm upgrade \
		--install \
		--namespace=$(NAMESPACE) \
		--set image.server=$(IMAGE) \
		--set ingress.server.domain=$(DOMAIN) \
		$(NAME) . \
		--dry-run \
		--debug

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
	sleep 2
	kubectl delete servers-test
