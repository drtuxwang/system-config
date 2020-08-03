NAME := xfce
IMAGE := drtuxwang/debian-xfce:stable

# Default namespace
ifndef NAMESPACE
	NAMESPACE=default
endif

# Default local port
ifndef LOCALPORT
	LOCALPORT=2222
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
		$(NAMESPACE)-$(NAME) ./xfce-servers

.PHONY: template
template:
	helm template --name=$(NAME) \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set image.name=$(IMAGE) \
		--set servers.ssh.pubkey="`cat ~/.ssh/id_rsa.pub`" \
		./xfce-servers

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
		$(NAMESPACE)-$(NAME) ./xfce-servers

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAMESPACE)-$(NAME)

.PHONY: forward
forward:
	kubectl --namespace $(NAMESPACE) port-forward service/$(NAME)-servers $(LOCALPORT):22

.PHONY: connect
connect:
	sleep 2 && svncviewer -p $(LOCALPORT) owner@localhost:5901 &
	make forward

.PHONY: version
version:
	@echo "`egrep "name|version:" Chart.yaml | awk '{printf("%s 	 ", $$2)}'` 	 $(IMAGE)"

.PHONY: delete
delete:
	helm ls $(NAMESPACE)-$(NAME)
	helm del --purge $(NAMESPACE)-$(NAME) ||:

.PHONY: clean
clean:
