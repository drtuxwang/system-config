NAME := xfce
CHART_REPO := .
CHART_NAME := xfce-servers
IMAGE := drtuxwang/debian-xfce:stable

# Default namespace
ifndef NAMESPACE
	NAMESPACE=default
endif

# Default local port
ifndef LOCALPORT
	LOCALPORT=
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
		--set servers.ssh.pubkey="`cat ~/.ssh/id_rsa.pub`" \
		$(NAMESPACE)-$(NAME) $(CHART_REPO)/$(CHART_NAME)

.PHONY: template
template:
	helm template --name=$(NAME) \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set image.name=$(IMAGE) \
		--set servers.ssh.pubkey="`cat ~/.ssh/id_rsa.pub`" \
		$(CHART_REPO)/$(CHART_NAME)

.PHONY: install
install:
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set image.name=$(IMAGE) \
		--set servers.ssh.pubkey="`cat ~/.ssh/id_rsa.pub`" \
		$(NAMESPACE)-$(NAME) $(CHART_REPO)/$(CHART_NAME)

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAMESPACE)-$(NAME)

.PHONY: forward
forward:
	kubectl --namespace=$(NAMESPACE) port-forward service/$(NAME)-servers $(LOCALPORT):22

.PHONY: connect
connect:
	./connect.sh

.PHONY: version
version:
	@grep "name:" $(CHART_NAME)/Chart.yaml | awk '{printf("./'$(CHART_NAME)'/%s   ", $$2)}'
	@grep "version:" $(CHART_NAME)/Chart.yaml | awk '{printf("%s   ", $$2)}'
	@grep "appVersion:" $(CHART_NAME)/Chart.yaml | awk '{printf("%s   ", $$2)}'
	@grep "description:" $(CHART_NAME)/Chart.yaml | cut -f2- -d" "

.PHONY: delete
delete:
	helm ls $(NAMESPACE)-$(NAME)
	helm del --purge $(NAMESPACE)-$(NAME) ||:

.PHONY: clean
clean:
