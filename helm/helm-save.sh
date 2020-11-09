#!/bin/bash -eu

if [ $# -lt 2 ]
then
    echo "Usage: $0 <tar-file> <docker-image>"
    exit 1
fi

FILE="$1"
shift

CREATED=$(docker inspect "$@" | sed -e 's/"/ /g' | sort -r | awk '/Created/ {print $3; exit}')

echo "docker save $@ -o $FILE"
docker save "$@" -o "$FILE"

echo "touch -d $CREATED $FILE"
touch -d $CREATED $FILE
