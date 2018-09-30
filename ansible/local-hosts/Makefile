HOST := hotdog.local

default: test

test:
	ansible-playbook --inventory=inventory/local-hosts setup-local.yml --limit $(HOST) --ask-become-pass --diff --check -K

run:
	ansible-playbook --inventory=inventory/local-hosts setup-local.yml --limit $(HOST) --ask-become-pass
