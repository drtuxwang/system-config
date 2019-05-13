NAMESPACE := ubuntu

default: status

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	kubectl --all-namespaces=true get pod -l name=tiller -o wide
	helm ls

.PHONY: install-tiller
install-tiller:
	kubectl -n kube-system create serviceaccount tiller
	kubectl create clusterrolebinding tiller --clusterrole cluster-admin --serviceaccount=kube-system:tiller
	helm init --service-account tiller

.PHONY: upgrade-tiller
upgrade-tiller:
	helm init --upgrade

.PHONY: uninstall-tiller
uninstall-tiller:
	kubectl -n kube-system delete serviceaccounts tiller ||:
	kubectl -n kube-system delete clusterrolebinding tiller ||:
	kubectl -n kube-system delete deploy tiller-deploy ||:
