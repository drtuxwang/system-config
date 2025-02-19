.PHONY: default
default: status       # Default

.PHONY: status
status:               # Show Kubernetes status
	kubectl --namespace=kube-system get pod
	@echo
	kubectl --namespace=kube-system get pod -o yaml | grep -E " image: " | grep -v "image: docker.io/" | sort | uniq
	@echo
	kubectl --namespace=kube-system exec -it `kubectl --namespace=kube-system get pod | grep "^etcd.*Running" | awk 'NR==1{print $1}'` -- etcdctl \
		--cert /etc/kubernetes/pki/etcd/peer.crt \
		--key /etc/kubernetes/pki/etcd/peer.key \
		--cacert /etc/kubernetes/pki/etcd/ca.crt \
		--endpoints 127.0.0.1:2379 \
		-w table endpoint status | \
		grep -v "+---"
	@echo
	kubectl get nodes -o wide

.PHONY: save
save:                 # Save Docker images used by Kubernetes to tar archive
	./bin/kube-save.bash
	ls -l *.tar*

.PHONY: clean
clean:                # Remove temporary build files
	rm -f kubernetes-images_*

.PHONY: help
help:                 # Show Makefile options
	@grep "^[A-Za-z0-9].*:" $(lastword $(MAKEFILE_LIST))
