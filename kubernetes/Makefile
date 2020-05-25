default: status

.PHONY: status
status:
	docker images | egrep "k8s.gcr.io|quay.io/coreos/flannel"
	@echo
	kubectl get nodes -o wide
	@echo
	kubectl --all-namespaces=true get pods | grep -v Running

.PHONY: save
save:
	docker save $(shell docker images | egrep "k8s.gcr.io|quay.io/coreos/flannel" | \
		awk '{printf("%s:%s\n", $$1, $$2)}') -o kubernetes.tar

.PHONY: load
load:
	for FILE in *.tar; do \
		 docker load -i $$FILE; \
	done
