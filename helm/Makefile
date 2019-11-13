NAMESPACE := ubuntu

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

.PHONY: install-tiller
install:
	kubectl -n kube-system create serviceaccount tiller
	kubectl create clusterrolebinding tiller --clusterrole cluster-admin --serviceaccount=kube-system:tiller
	helm init --service-account tiller

.PHONY: upgrade-tiller
replace:
	helm init --upgrade

.PHONY: uninstall-tiller
uninstall:
	kubectl -n kube-system delete serviceaccounts tiller ||:
	kubectl -n kube-system delete clusterrolebinding tiller ||:
	kubectl -n kube-system delete deploy tiller-deploy ||:
