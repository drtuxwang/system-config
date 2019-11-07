NAME := jenkins-server
VERSION := 3.4.2

# Default namespace
ifndef NAMESPACE
	NAMESPACE=default
endif


default: status

.PHONY: check
check:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		--namespace=$(NAMESPACE) \
		--set fullnameOverride=$(NAME) \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--set persistence.enabled=false \
		--set service.type=ClusterIP \
		--version $(VERSION) \
		$(NAMESPACE)-$(NAME) bitnami/jenkins

.PHONY: install
install:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--set fullnameOverride=$(NAME) \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--set persistence.enabled=false \
		--set service.type=ClusterIP \
		--version $(VERSION) \
		$(NAMESPACE)-$(NAME) bitnami/jenkins

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAMESPACE)-$(NAME)

.PHONY: connect
connect:
	@echo "\n*** Connecting to Jenkins server ***"
	@echo "Username: user"
	@kubectl get secret --namespace $(NAMESPACE) $(NAME) -o jsonpath="{.data.jenkins-password}" | \
		base64 -d | awk '{printf("Password: %s\n", $$1)}'
	@echo "firefox http://`kubectl get service jenkins-server | awk 'NR==2 {print $$3}'`"
	@firefox http://`kubectl get service jenkins-server | awk 'NR==2 {print $$3}'`

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAMESPACE)-$(NAME) ||:
