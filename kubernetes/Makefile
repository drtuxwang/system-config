default: status

.PHONY: status
status:
	kubectl get pod -n kube-system
	@echo
	kubectl pod -n kube-system -o yaml | grep " image:" | sort | uniq
	@echo
	kubectl exec -n kube-system -it `kubectl get pod -n kube-system | grep "^etcd.*Running" | awk 'NR==1{print $1}'` -- etcdctl \
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
