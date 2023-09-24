#!/usr/bin/env bash
#
# Load Docker images from "tar|tar.*|t[bgx]z" archives
#

set -eu

if [ $# = 0 ]
then
    echo "Usage: $0 <image>"
    exit 1
fi

while [ $# != 0 ]
do
    FILE="$1"
    case "$FILE" in
    *.list)
        ;;
    *.tar.7z|*.t7z)
        echo "7z x -so \"$FILE\" | docker load"
        7z x -so "$FILE" | docker load
        ;;
    *.tar|*.tar.*|*.t[bgx]z)
        echo "docker load -i \"$FILE\""
        docker load -i "$FILE"
        ;;
    esac
    shift
done