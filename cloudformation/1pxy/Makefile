# PHONY targets
.PHONY: test pep8

default: test

test: pep8
	@echo "\n*** Tests successfull ***"

pep8:
	@echo "\n*** Running JSON PEP8 check ***"
	python3 -m pep8 --max-line-length=255 *.json
