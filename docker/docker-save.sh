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
    LIST="${FILE%.tar}.list"
    CREATED=$(docker inspect "$IMAGE" | sed -e 's/"/ /g' | sort -r | awk '/Created/ {print $3; exit}')

    echo "docker save $@ -o $FILE"
    docker save "$@" -o "$FILE.part"
    tar xf "$FILE.part" repositories -O | sed -e "s/,/\\n/g;s/\"/:/g" | cut -f2,5 -d: > "$LIST.part"
    touch -d $CREATED "$FILE.part" "$LIST.part"
    mv "$FILE.part" "$FILE"
    mv "$LIST.part" "$LIST"
done
