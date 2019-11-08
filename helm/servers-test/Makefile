NAME := servers-test
IMAGE := drtuxwang/debian-bash
DOMAIN := example.com

# Default namespace
ifndef NAMESPACE
	NAMESPACE=default
endif

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
		--set fullnameOverride=$(NAME) \
		--set image.name=$(IMAGE) \
		--set ingress.server.domain=$(DOMAIN) \
		$(NAMESPACE)-$(NAME) .

.PHONY: template
template:
	helm template --name=$(NAME) \
		--namespace=$(NAMESPACE) \
		--set fullnameOverride=$(NAME) \
		--set image.name=$(IMAGE) \
		--set ingress.server.domain=$(DOMAIN) \
		.

.PHONY: deploy
deploy:
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--set fullnameOverride=$(NAME) \
		--set image.name=$(IMAGE) \
		--set ingress.server.domain=$(DOMAIN) \
		$(NAMESPACE)-$(NAME) .

.PHONY: forward
forward:
	kubectl --namespace $(NAMESPACE) describe service/$(NAME)-server
	kubectl --namespace $(NAMESPACE) port-forward service/$(NAME)-server $(LOCALPORT):80

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAMESPACE)-$(NAME)

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAMESPACE)-$(NAME) ||:
