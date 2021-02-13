#!/bin/bash -eu

if [ $# -lt 4 ]
then
    echo "Usage: $0 <chart> <chart-version> <app> <docker-image>"
    exit 1
fi

FILE="../helm-images_${1#*/}_${2}_app-${3}.tar"
shift 3

CREATED=$(docker inspect "$@" | sed -e 's/"/ /g' | sort -r | awk '/Created/ {print $3; exit}')

echo "docker save $@ -o $FILE"
docker save "$@" -o "$FILE"

echo "touch -d $CREATED $FILE"
touch -d $CREATED $FILE
