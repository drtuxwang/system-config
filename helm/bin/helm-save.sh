#!/usr/bin/env bash
#
# Save images used by Helm release as tar archive
#

set -eu

if [ $# -lt 4 ]
then
    echo "Usage: $0 <chart-name> <chart-version> <app-version> <image1> [<image2] ...]"
    exit 1
fi

umask 022

FILE="../${1#*/}_${2}_app-${3}.tar"
shift 3
CREATED=$(docker inspect "$@" | sed -e 's/"/ /g' | sort -r | awk '/Created/ {print $3; exit}')

if [ -f "$FILE.7z" ]
then
    echo "Skipping existing file: $(realpath $FILE.7z)"
else
    echo "docker save $@ -o $FILE"
    docker save "$@" -o "$FILE.part"
    tar xf "$FILE.part" repositories -O | sed -e "s/,/\\n/g;s/\"/:/g" | cut -f2,5 -d: > "$FILE.list.part"
    touch -d $CREATED "$FILE.part" "$FILE.list.part"
    mv "$FILE.part" "$FILE"
    mv "$FILE.list.part" "$FILE.list"
    7z a -m0=lzma2 -mmt=2 -mx=9 -myx=9 -md=128m -mfb=256 -ms=on -snh -snl -stl -y "$FILE.7z.part" "$FILE"
    mv "$FILE.7z.part" "$FILE.7z"
    rm "$FILE"
    echo "Created archive file: $(realpath $FILE.7z)"
fi
