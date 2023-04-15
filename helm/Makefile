BUILD_DIRS := \
	cassandra \
	etcd \
	grafana \
	jenkins \
	kafka \
	mongodb \
	nexus \
	nginx \
	oracle-xe \
	postgresql \
	prometheus \
	pushgateway \
	rabbitmq \
	test-box \
	test-server \
	xfce-server


ifeq ($(shell helm version | grep -c v3), 1)
	HELM_INIT :=
	HELM_LIST := helm --all-namespaces=true list --all
else
	HELM_INIT := helm init --client-only
	HELM_LIST := helm list --all
endif


.PHONY: default
default: status      # Default

.PHONY: status
status:              # Status of Helm release
	$(HELM_INIT)
	@echo "\n*** Helm client-server status ***"
	helm version
	@echo "\n*** Helm repositories ***"
	helm repo list
	@echo "\n*** Helm releases ***"
	$(HELM_LIST)

.PHONY: update
update:              # Update Helm chart repository
	helm repo list | grep -q bitnami || helm repo add bitnami https://charts.bitnami.com/bitnami
	helm repo list | grep -q ingress-nginx || helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
	helm repo list | grep -q oteemo || helm repo add oteemo https://oteemo.github.io/charts
	helm repo list | grep -q prometheus-community || helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
	helm repo update

.PHONY: version
version:             # Helm chart versions
	@for DIR in $(BUILD_DIRS); do \
		make --no-print-directory --directory $$DIR version | sed -e "s/^/$$DIR: /"; \
	done

.PHONY: images
images:              # Show Docker images
	@for DIR in $(BUILD_DIRS); do \
		make --no-print-directory --directory $$DIR images || exit 1; \
	done

.PHONY: pull
pull:                # Pull Docker images
	@for DIR in $(BUILD_DIRS); do \
		make --no-print-directory --directory $$DIR pull || exit 1; \
	done

.PHONY: save
save:                # Save Docker images as tar file
	@for DIR in $(BUILD_DIRS); do \
		make --no-print-directory --directory $$DIR save || exit 1; \
	done
	ls -l *.tar*

.PHONY: install-tiller
install-tiller:      # Install legacy Helm 2.x server
	kubectl --namespace=kube-system create serviceaccount tiller
	kubectl create clusterrolebinding tiller --clusterrole cluster-admin --serviceaccount=kube-system:tiller
	helm init --service-account tiller

.PHONY: upgrade-tiller
upgrade-tiller:      # Upgrade legacy Helm 2.x server
	helm init --upgrade

.PHONY: uninstall-tiller
uninstall-tiller:    # Uninstall legacy Helm 2.x server
	kubectl --namespace=kube-system delete serviceaccounts tiller ||:
	kubectl --namespace=kube-system delete clusterrolebinding tiller ||:
	kubectl --namespace=kube-system delete deploy tiller-deploy ||:

.PHONY: clean
clean:               # Remove temporary build files
	rm -f helm-images_*
	for DIR in $(BUILD_DIRS); do \
		make --no-print-directory --directory $$DIR clean; \
	done

.PHONY: rmi
rmi:                 # Remove Docker images
	for DIR in $(BUILD_DIRS); do \
		make --no-print-directory --directory $$DIR rmi; \
	done

.PHONY: help
help:                # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
