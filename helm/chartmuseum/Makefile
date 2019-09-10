NAME := chartmuseum
NAMESPACE := default
INGRESS_HOST := chartmusuem.local
SECRET := chartmusuem-secret-tls


default: status

.PHONY: check
check:
	helm repo add stable https://kubernetes-charts.storage.googleapis.com
	helm install -n $(NAME) \
		--namespace=$(NAMESPACE) \
		--set persistence.enabled=false \
		--set env.open.DISABLE_API=false \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--set persistence.enabled=true \
		--set ingress.enabled=true \
		--set ingress.hosts[0].name=$(INGRESS_HOST) \
		--set ingress.hosts[0].tls=true \
		--set ingress.hosts[0].tlsSecret=$(SECRET) \
		stable/chartmuseum
		--dry-run \
		--debug

.PHONY: install
install:
	helm repo add stable https://kubernetes-charts.storage.googleapis.com
	helm install -n $(NAME) \
		--namespace=$(NAMESPACE) \
		--set persistence.enabled=false \
		--set env.open.DISABLE_API=false \
		--set nodeSelector."beta\.kubernetes\.io/os"=linux \
		--set persistence.enabled=true \
		--set ingress.enabled=true \
		--set ingress.hosts[0].name=$(INGRESS_HOST) \
		--set ingress.hosts[0].tls=true \
		--set ingress.hosts[0].tlsSecret=$(SECRET) \
		stable/chartmuseum
	sleep 2
	kubectl --namespace=$(NAMESPACE) get all

.PHONY: upgrade
upgrade:
	helm upgrade $(NAME) .

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm ls
	@echo
	kubectl --namespace=$(NAMESPACE) get all -o wide

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAME) ||:
