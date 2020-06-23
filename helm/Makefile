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
	ops-box \
	oracle-xe \
	pushgateway \
	rabbitmq \
	servers-test


default: status

.PHONY: status
status:
	@echo "\n*** Helm client initialize ***"
	helm init --client-only
	@echo "\n*** Helm client-server status ***"
	helm version
	@echo "\n*** Helm repositories ***"
	helm repo list
	@echo "\n*** Helm releases ***"
	helm list

.PHONY: pull
pull:
	helm repo update

.PHONY: version
version:
	@for DIR in $(BUILD_DIRS); do \
		make --no-print-directory -C $$DIR version || exit 1; \
	done

.PHONY: install-tiller
install-tiller:
	kubectl -n kube-system create serviceaccount tiller
	kubectl create clusterrolebinding tiller --clusterrole cluster-admin --serviceaccount=kube-system:tiller
	helm init --service-account tiller

.PHONY: upgrade-tiller
replace:
	helm init --upgrade

.PHONY: uninstall-tiller
uninstall-tiller:
	kubectl -n kube-system delete serviceaccounts tiller ||:
	kubectl -n kube-system delete clusterrolebinding tiller ||:
	kubectl -n kube-system delete deploy tiller-deploy ||:

.PHONY: clean
clean:
	for DIR in $(BUILD_DIRS); do \
		make -C $$DIR clean; \
	done
