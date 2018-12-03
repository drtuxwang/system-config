NAMESPACE := ubuntu
IMAGE := ubuntu:18.04
NAME := server-test

default: check

.PHONY: check
check:
	helm install --namespace=$(NAMESPACE) -n $(NAME) --set image.server=$(IMAGE) . --dry-run --debug

.PHONY: install
install:
	helm install --namespace=$(NAMESPACE) -n $(NAME) --set image.server=$(IMAGE) .
	sleep 2
	kubectl --namespace=$(NAMESPACE) get all

.PHONY: upgrade
upgrade:
	helm upgrade $(NAME) .
	sleep 2
	kubectl --namespace$(NAMESPACE) get all

.PHONY: forward
forward:
	kubectl --namespace $(NAMESPACE) describe service/$(NAME)-mychart-server
	kubectl --namespace $(NAMESPACE) port-forward service/$(NAME)-mychart-server 8080:80

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	kubectl --namespace=$(NAMESPACE) get all

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAME) ||:

.PHONY: install-tiller
install-tiller:
	kubectl -n kube-system create serviceaccount tiller
	kubectl create clusterrolebinding tiller --clusterrole cluster-admin --serviceaccount=kube-system:tiller
	helm init --service-account tiller
