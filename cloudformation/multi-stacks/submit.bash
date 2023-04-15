#!/usr/bin/env bash
#
# Nested stacks CloudFormation submission
#
STACKNAME="pxy-example"
STACKDIR="mybucket-f265e99a/$STACKNAME"

aws s3 sync . s3://$STACKDIR

aws cloudformation create-stack --stack-name "$STACKNAME" \
    --template-body file://$PWD/main_stack.json
