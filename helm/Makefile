#
# helm search -l <chart-name>
# helm fetch --version <version> <chart-name>
# helm dep update
#
BUILD_DIRS := \
	chartmuseum \
	concourse \
	etcd \
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
	HELM_INIT=
	HELM_LIST=helm list --all-namespaces --all
else
	HELM_INIT=helm init --client-only
	HELM_LIST=helm list --all
endif


default: status

.PHONY: status
status:
	$(HELM_INIT)
	@echo "\n*** Helm client-server status ***"
	helm version
	@echo "\n*** Helm repositories ***"
	helm repo list
	@echo "\n*** Helm releases ***"
	$(HELM_LIST)

.PHONY: update
update:
	helm repo list | grep -q stable || helm repo add stable https://charts.helm.sh/stable
	helm repo list | grep -q bitnami || helm repo add bitnami https://charts.bitnami.com/bitnami
	helm repo list | grep -q concourse || helm repo add concourse https://concourse-charts.storage.googleapis.com
	helm repo list | grep -q ingress-nginx || helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
	helm repo list | grep -q oteemo || helm repo add oteemo https://oteemo.github.io/charts
	helm repo list | grep -q prometheus-community || helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
	helm repo update

.PHONY: images
images:
	@for DIR in $(BUILD_DIRS); do \
		make -C $$DIR images || exit 1; \
	done

.PHONY: pull
pull:
	@for DIR in $(BUILD_DIRS); do \
		make -C $$DIR pull || exit 1; \
	done

.PHONY: save
save:
	@for DIR in $(BUILD_DIRS); do \
		make -C $$DIR save || exit 1; \
	done

.PHONY: version
version:
	@for DIR in $(BUILD_DIRS); do \
		make -C $$DIR version || exit 1; \
	done

.PHONY: install-tiller
install-tiller:
	kubectl create -n kube-system serviceaccount tiller
	kubectl create clusterrolebinding tiller --clusterrole cluster-admin --serviceaccount=kube-system:tiller
	helm init --service-account tiller

.PHONY: upgrade-tiller
upgrade-tiller:
	helm init --upgrade

.PHONY: uninstall-tiller
uninstall-tiller:
	kubectl delete -n kube-system serviceaccounts tiller ||:
	kubectl delete -n kube-system clusterrolebinding tiller ||:
	kubectl delete -n kube-system deploy tiller-deploy ||:

.PHONY: clean
clean:
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR clean; \
	done
