#!/usr/bin/env bash
#
# Save Docker images used  by Helm release
#

set -eu

if [ $# -lt 4 ]
then
    echo "Usage: $0 <chart> <chart-version> <app> <docker-image>"
    exit 1
fi

FILE="../helm-images_${1#*/}_${2}_app-${3}.tar"
shift 3
LIST="${FILE%.tar}.list"
CREATED=$(docker inspect "$@" | sed -e 's/"/ /g' | sort -r | awk '/Created/ {print $3; exit}')

echo "docker save $@ -o $FILE"
docker save "$@" -o "$FILE.part"
tar xf "$FILE.part" repositories -O | sed -e "s/,/\\n/g;s/\"/:/g" | cut -f2,5 -d: > "$LIST.part"
touch -d $CREATED "$FILE.part" "$LIST.part"
mv "$FILE.part" "$FILE"
mv "$LIST.part" "$LIST"
