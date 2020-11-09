#!/bin/bash -eu

if [ $# = 0 ]
then
    echo "Usage: $0 <docker-image>"
    exit 1
fi

for FILE in $*
do
    echo "docker load -i $FILE"
    docker load -i $FILE
done
