default: status

.PHONY: status
status:
	kubectl --namespace=kube-system get pod
	@echo
	kubectl --namespace=kube-system pod -o yaml | grep " image:" | sort | uniq
	@echo
	kubectl --namespace=kube-system exec -it `kubectl --namespace=kube-system get pod | grep "^etcd.*Running" | awk 'NR==1{print $1}'` -- etcdctl \
		--cert /etc/kubernetes/pki/etcd/peer.crt \
		--key /etc/kubernetes/pki/etcd/peer.key \
		--cacert /etc/kubernetes/pki/etcd/ca.crt \
		--endpoints 127.0.0.1:2379 \
		-w table endpoint status
	@echo
	kubectl get nodes -o wide

.PHONY: save
save:
	./kubernetes-save.sh

.PHONY: load
load:
	for FILE in *.tar; do \
		 docker load -i $$FILE; \
	done
