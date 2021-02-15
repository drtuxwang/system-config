#!/bin/bash -eu

if [ $# = 0 ]
then
    echo "Usage: $0 <docker-image>"
    exit 1
fi

for FILE in $*
do
    case $FILE in
    *.tar|*.tar.*|*.t[bgx]z)
        echo "docker load -i $FILE"
        docker load -i $FILE
        ;;
    esac
done
