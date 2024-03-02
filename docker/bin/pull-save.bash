#!/usr/bin/env bash
#
# Pull updated Docker images and save to tar archives
#

set -eu

if [ $# = 0 ]
then
    echo "Usage: $0 <image>"
    exit 1
fi

for IMAGE in $*;
do
    CREATED_OLD=$(docker inspect "$IMAGE" | sed -e 's/"/ /g' | sort -r | awk '/Created/ {print $3; exit}')
    docker pull $IMAGE
    CREATED=$(docker inspect "$IMAGE" | sed -e 's/"/ /g' | sort -r | awk '/Created/ {print $3; exit}')
    if [ "$CREATED_OLD" != "$CREATED" ]
    then
        $(dirname "$0")/../../bin/docker-save "$IMAGE"
    fi
done
