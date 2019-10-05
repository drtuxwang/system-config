NAME := jenkins-server
VERSION := 3.4.2
NAMESPACE := default

default: status

.PHONY: check
check:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		--namespace=$(NAMESPACE) \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--set persistence.enabled=false \
		--version $(VERSION) \
		$(NAME) --wait bitnami/jenkins

# Can't use --wait due to LoadBalancer not assigned external-IP
.PHONY: install
install:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm upgrade \
		--install \
		--namespace=$(NAMESPACE) \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--set persistence.enabled=false \
		--version $(VERSION) \
		$(NAME) bitnami/jenkins

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAME)

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAME) ||:
