#!/usr/bin/env bash

set -e


for FILE in ${0%/*}/get*.bash
do
    echo -e "\033[33mChecking: ${FILE##*/}\033[0m"
    $FILE --check
done
