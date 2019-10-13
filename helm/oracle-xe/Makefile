NAME := oracle-server
IMAGE := datagrip/oracle:11.2
NAMESPACE := default

default: status

.PHONY: check
check:
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		--namespace=$(NAMESPACE) \
		--set image.name=$(IMAGE) \
		$(NAME) .

.PHONY: template
template:
	helm template --name=$(NAME) \
		--set image.name=$(IMAGE) \
		.

.PHONY: install
install:
	helm upgrade \
		--install \
		--wait \
		--namespace=$(NAMESPACE) \
		--set image.name=$(IMAGE) \
		$(NAME) .

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAME)

.PHONY: connect
connect:
	@echo "\n*** Connecting to Oracle XE database ***"
	@echo sqlplus system/oracle@`kubectl get service oracle-server-oracle | awk 'NR==2 {print $$3}'`
	@sqlplus system/oracle@`kubectl get service oracle-server-oracle | awk 'NR==2 {print $$3}'`

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAME) ||:
