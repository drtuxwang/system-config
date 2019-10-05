NAME := concourse-server
VERSION := 8.2.3
NAMESPACE := default

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
		--set persistence.enabled=false \
		--version $(VERSION) \
		$(NAME) --wait stable/concourse

.PHONY: install
install:
	# Can't use --wait due to external IP pending
	helm upgrade \
		--install \
		--namespace=$(NAMESPACE) \
		--set persistence.enabled=false \
		--set postgresql.persistence.enabled=false \
		--version $(VERSION) \
		$(NAME) stable/concourse

.PHONY: forward
forward:
	kubectl --namespace $(NAMESPACE) port-forward service/concourse-web $(LOCALPORT):8080

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAME)

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAME) ||:
	sleep 2
	kubectl delete namespace concourse-server-main
