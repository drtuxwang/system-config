#!/usr/bin/env bash

set -eu

FILES=$(ls -1 ${0%/*}/get*.bash)
[ ${1:-} ] && FILES=$(realpath $1 2> /dev/null)

for FILE in $FILES
do
    echo -e "\033[33mChecking: ${FILE##*/}\033[0m"
    $FILE --check
done
