#!/bin/bash -eu

if [ $# = 0 ]
then
    echo "Usage: $0 <docker-image>"
    exit 1
fi

cd $(dirname $0)

for IMAGE in $*;
do
    HASH=$(docker images | sed -e "s/  */:/" | grep "^$IMAGE " | awk '{print $2}')
    FILE=docker-image_$(echo $IMAGE | sed -e "s/\//-/g;s/:/_/")_$HASH.tar
    CREATED=$(docker inspect "$IMAGE" | sed -e 's/"/ /g' | sort -r | awk '/Created/ {print $3; exit}')

    echo "docker save $@ -o $FILE"
    docker save "$@" -o "$FILE.part"
    touch -d $CREATED "$FILE.part"
    mv "$FILE.part" "$FILE"
done
