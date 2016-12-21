HOST := rocky

default: test

test:
	ansible-playbook --inventory=hosts setup-test.yml --limit $(HOST) --diff --check

run:
	ansible-playbook --inventory=hosts setup-test.yml --limit $(HOST)
