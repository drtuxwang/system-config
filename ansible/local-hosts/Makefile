HOST := hotdog.local

default: test

test:
	ansible-playbook --inventory=inventory/local-hosts setup-local.yml --limit $(HOST) --diff --check

run:
	ansible-playbook --inventory=inventory/local-hosts setup-local.yml --limit $(HOST)
