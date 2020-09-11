default: status

.PHONY: status
status:
	kubectl -n kube-system exec -it `kubectl -n kube-system get pod | grep "^etcd.*Running" | awk 'NR==1{print $1}'` -- etcdctl \
		--cert /etc/kubernetes/pki/etcd/peer.crt \
		--key /etc/kubernetes/pki/etcd/peer.key \
		--cacert /etc/kubernetes/pki/etcd/ca.crt \
		--endpoints 127.0.0.1:2379 \
		-w table endpoint status
	@echo
	kubectl -n kube-system get pod -o yaml | grep " image:" | sort | uniq
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
