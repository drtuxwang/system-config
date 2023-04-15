#!/usr/bin/env bash

cd ${0%/*}/..

for FILE in $(find * \( -name "*.yaml" -o -name "*.yml" \) | sort)
do
    sed ':a;N;$!ba;s/\n *- */ /g' $FILE | grep tags: | sed -e "s/.*tags: //;s/ /\\n/" | \
        sort | uniq | sed -e "s@^@$FILE: @"
done
