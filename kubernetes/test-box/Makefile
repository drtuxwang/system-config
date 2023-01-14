NAME :=test-box
CONFIG := cat $(NAME).yaml

ifndef NAMESPACE
	NAMESPACE := default
endif

ifdef HOSTNAME
	CONFIG := sed -e "s@.*kubernetes.io/hostname:.*@        kubernetes.io/hostname: $(HOSTNAME)@" $(NAME).yaml
endif


.PHONY: default
default: status      # Default

.PHONY: status
status:              # Show workload status
	@echo "\n*** Checking Kube status ***"
	@make --no-print-directory status-kube | sort
	@echo

.PHONY: status-kube
status-kube:         # Show Kube workload status
	@kubectl --namespace=$(NAMESPACE) get all -o wide 2> /dev/null | grep "$(NAME)" | sed -e "s/^/$(NAMESPACE)   /" ||:

.PHONY: create
create:              # Create workload
	@echo "\n*** Creating pod ***"
	$(CONFIG) | kubectl --namespace=$(NAMESPACE) create -f - ||:

.PHONY: run
run:                 # Run interactive pod
	@echo "\n*** Running interactive pod ***"
	kubectl --namespace=$(NAMESPACE) run -it --rm --restart='Never' --image drtuxwang/debian-bash $(NAME)

.PHONY: delete
delete:              # Delete workload
	@echo "\n*** Removing pod ***"
	kubectl --namespace=$(NAMESPACE) delete -f $(NAME).yaml ||:

.PHONY: help
help:                # Show Makefile options
	@grep -E "^[A-Za-z0-9_-]+:" $(lastword $(MAKEFILE_LIST))
