#!/usr/bin/env bash
#
# Save Docker images to tar archives
#

set -eu

if [ $# = 0 ]
then
    echo "Usage: $0 <docker-image>"
    exit 1
fi

cd $(dirname $0)

for IMAGE in $*;
do
    CREATED=$(docker inspect "$IMAGE" | sed -e 's/"/ /g' | sort -r | awk '/Created/ {print $3; exit}')
    FILE=../docker-image_$(echo $IMAGE | sed -e "s/\//-/g;s/:/_/")_$(echo $CREATED | sed -e "s/-//g;s/T.*//").tar
    LIST="${FILE%.tar}.list"

    echo "docker save $@ -o $FILE"
    docker save "$@" -o "$FILE.part"
    tar xf "$FILE.part" repositories -O | sed -e "s/,/\\n/g;s/\"/:/g" | cut -f2,5 -d: > "$LIST.part"
    touch -d $CREATED "$FILE.part" "$LIST.part"
    mv "$FILE.part" "$FILE"
    mv "$LIST.part" "$LIST"
done
