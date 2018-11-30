default: check

.PHONY: check
check:
	helm install -n server-test --namespace server . --dry-run --debug

.PHONY: install
install:
	helm install -n ubuntu-test --namespace ubuntu --set image.server=ubuntu:18.04 .
	sleep 2
	kubectl --namespace ubuntu get all

.PHONY: clean
clean:
	helm ls
	helm del --purge ubuntu-test ||:

.PHONY: install-tiller
install-tiller:
	kubectl -n kube-system create serviceaccount tiller
	kubectl create clusterrolebinding tiller --clusterrole cluster-admin --serviceaccount=kube-system:tiller
	helm init --service-account tiller
