#!/usr/bin/env bash
#
# Pull Docker images and save to tar archives
#

set -eu

if [ $# = 0 ]
then
    echo "Usage: $0 <image>"
    exit 1
fi

cd $(dirname $0)

for IMAGE in $*;
do
    CREATED_OLD=$(docker inspect "$IMAGE" | sed -e 's/"/ /g' | sort -r | awk '/Created/ {print $3; exit}')
    docker pull $IMAGE
    CREATED=$(docker inspect "$IMAGE" | sed -e 's/"/ /g' | sort -r | awk '/Created/ {print $3; exit}')
    if [ "$CREATED_OLD" != "$CREATED" ]
    then
        $(dirname "$0")/docker-save.bash "$IMAGE"
    fi
done
