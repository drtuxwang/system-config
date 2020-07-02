NAME := test
IMAGE := drtuxwang/debian-bash:10
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
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set image.name=$(IMAGE) \
		--set ingress.server.domain=$(DOMAIN) \
		$(NAMESPACE)-$(NAME) ./test-servers

.PHONY: template
template:
	helm template --name=$(NAME) \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set image.name=$(IMAGE) \
		--set ingress.server.domain=$(DOMAIN) \
		./test-servers

.PHONY: install
install:
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set image.name=$(IMAGE) \
		--set ingress.server.domain=$(DOMAIN) \
		$(NAMESPACE)-$(NAME) ./test-servers

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAMESPACE)-$(NAME)

.PHONY: version
version:
	@echo "`egrep "name|version:" Chart.yaml | awk '{printf("%s 	 ", $$2)}'` 	 $(IMAGE)"

.PHONY: forward
forward:
	kubectl --namespace $(NAMESPACE) port-forward service/$(NAME)-server $(LOCALPORT):80

.PHONY: connect
connect:
	sleep 2 && firefox http://127.0.0.1:$(LOCALPORT) &
	make forward

.PHONY: delete
delete:
	helm ls $(NAMESPACE)-$(NAME)
	helm del --purge $(NAMESPACE)-$(NAME) ||:

.PHONY: clean
clean:
