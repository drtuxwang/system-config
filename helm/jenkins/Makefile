NAME := jenkins-server
VERSION := 4.0.4

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
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
		--set service.type=ClusterIP \
		--version $(VERSION) \
		$(NAMESPACE)-$(NAME) bitnami/jenkins

.PHONY: deploy
deploy:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--values values.yaml \
		--set fullnameOverride=$(NAME) \
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

.PHONY: version
version:
	@helm search -l bitnami/jenkins | grep "bitnami/jenkins	*$(VERSION) "

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAMESPACE)-$(NAME) ||:
