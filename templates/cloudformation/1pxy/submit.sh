#!/bin/sh

STACKNAME="1pxy-example"

aws cloudformation create-stack --stack-name "$STACKNAME" \
    --template-body file://$PWD/main_stack.json
