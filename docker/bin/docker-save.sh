#!/usr/bin/env bash
#
# Save images as tar archives
#

set -eu

if [ $# = 0 ]
then
    echo "Usage: $0 <image>"
    exit 1
fi

cd $(dirname $0)
umask 022

for IMAGE in $*;
do
    CREATED=$(docker inspect "$IMAGE" | sed -e 's/"/ /g' | sort -r | awk '/Created/ {print $3; exit}')
    FILE=../$(echo $IMAGE | sed -e "s/\//-/g;s/:/_/")_$(echo $CREATED | sed -e "s/-//g;s/T.*//").tar
    LIST="${FILE%.tar}.list"

    if [ -f "$FILE.7z" ]
    then
        echo "Skipping existing file: $(realpath $FILE.7z)"
    else
        echo "docker save $@ -o $FILE"
        docker save "$@" -o "$FILE.part"
        tar xf "$FILE.part" repositories -O | sed -e "s/,/\\n/g;s/\"/:/g" | cut -f2,5 -d: > "$LIST.part"
        touch -d $CREATED "$FILE.part" "$LIST.part"
        mv "$FILE.part" "$FILE"
        mv "$LIST.part" "$LIST"
        7z a -m0=lzma2 -mmt=2 -mx=9 -myx=9 -md=128m -mfb=256 -ms=on -snh -snl -stl -y "$FILE.7z.part" "$FILE"
        mv "$FILE.7z.part" "$FILE.7z"
        rm "$FILE"
        echo "Created archive file: $(realpath $FILE.7z)"
    fi
    shift
done
