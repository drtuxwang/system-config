ifndef HOST
	HOST=hotdog.local
endif

default: test

test:
	ansible-playbook --inventory=inventory/local-hosts setup-local.yml --limit $(HOST) --ask-become-pass --diff --check

run:
	ansible-playbook --inventory=inventory/local-hosts setup-local.yml --limit $(HOST) --ask-become-pass
