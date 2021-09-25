BUILD_DIRS := \
	chartmuseum \
	concourse \
	etcd \
	grafana \
	ingress-controller \
	jenkins \
	kafka \
	mongodb \
	nexus \
	nginx \
	ops-server \
	oracle-xe \
	prometheus \
	pushgateway \
	rabbitmq \
	test-server \
	xfce-server

ifeq ($(shell helm version | grep -c v3), 1)
	HELM_INIT :=
	HELM_LIST := helm --all-namespaces=true list --all
else
	HELM_INIT := helm init --client-only
	HELM_LIST := helm list --all
endif


default: status

.PHONY: status
status:       # Status of Helm release
	$(HELM_INIT)
	@echo "\n*** Helm client-server status ***"
	helm version
	@echo "\n*** Helm repositories ***"
	helm repo list
	@echo "\n*** Helm releases ***"
	$(HELM_LIST)

.PHONY: update
update:       # Update Helm chart repository
	helm repo list | grep -q stable || helm repo add stable https://charts.helm.sh/stable
	helm repo list | grep -q bitnami || helm repo add bitnami https://charts.bitnami.com/bitnami
	helm repo list | grep -q concourse || helm repo add concourse https://concourse-charts.storage.googleapis.com
	helm repo list | grep -q ingress-nginx || helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
	helm repo list | grep -q oteemo || helm repo add oteemo https://oteemo.github.io/charts
	helm repo list | grep -q prometheus-community || helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
	helm repo update

.PHONY: version
version:      # Helm chart versions
	@for DIR in $(BUILD_DIRS); do \
		make -C $$DIR version || exit 1; \
	done

.PHONY: images
images:       # Show Docker images
	@for DIR in $(BUILD_DIRS); do \
		make -C $$DIR images || exit 1; \
	done

.PHONY: pull
pull:         # Pull Docker images
	@for DIR in $(BUILD_DIRS); do \
		make -C $$DIR pull || exit 1; \
	done

.PHONY: save
save:         # Save Docker images as tar file
	@for DIR in $(BUILD_DIRS); do \
		make -C $$DIR save || exit 1; \
	done

.PHONY: install-tiller
install-tiller: # Install legacy Helm 2.x server
	kubectl --namespace=kube-system create serviceaccount tiller
	kubectl create clusterrolebinding tiller --clusterrole cluster-admin --serviceaccount=kube-system:tiller
	helm init --service-account tiller

.PHONY: upgrade-tiller
upgrade-tiller: # Upgrade legacy Helm 2.x server
	helm init --upgrade

.PHONY: uninstall-tiller
uninstall-tiller: # Uninstall legacy Helm 2.x server
	kubectl --namespace=kube-system delete serviceaccounts tiller ||:
	kubectl --namespace=kube-system delete clusterrolebinding tiller ||:
	kubectl --namespace=kube-system delete deploy tiller-deploy ||:

.PHONY: clean
clean:        # Remove temporary build files
	rm -f helm-images_*
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR clean; \
	done

.PHONY: rmi
rmi:          # Remove Docker images
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR rmi; \
	done

.PHONY: help
help:
	@egrep "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
