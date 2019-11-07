NAME := ops
IMAGE := drtuxwang/debian-bash

# Default namespace
ifndef NAMESPACE
	NAMESPACE=default
endif

default: status

.PHONY: check
check:
	helm upgrade \
		--install \
		--dry-run \
		--debug \
		--namespace=$(NAMESPACE) \
		--set release.name=$(NAME) \
		--set image.name=$(IMAGE) \
		$(NAMESPACE)-$(NAME) .

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
		--set release.name=$(NAME) \
		--set image.name=$(IMAGE) \
		$(NAMESPACE)-$(NAME) .

.PHONY: status
status:
	@echo "\n*** Checking status ***"
	helm status $(NAMESPACE)-$(NAME)

.PHONY: clean
clean:
	helm ls
	helm del --purge $(NAMESPACE)-$(NAME) ||:
