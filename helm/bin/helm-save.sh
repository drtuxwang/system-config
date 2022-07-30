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

FILE="../${1#*/}_${2}_app-${3}.tar"
shift 3
LIST="${FILE%.tar}.list"
CREATED=$(docker inspect "$@" | sed -e 's/"/ /g' | sort -r | awk '/Created/ {print $3; exit}')

echo "docker save $@ -o $FILE"
docker save "$@" -o "$FILE.part"
tar xf "$FILE.part" repositories -O | sed -e "s/,/\\n/g;s/\"/:/g" | cut -f2,5 -d: > "$LIST.part"
touch -d $CREATED "$FILE.part" "$LIST.part"
chmod 644 "$FILE.part"
mv "$FILE.part" "$FILE"
mv "$LIST.part" "$LIST"
