#!/bin/bash

connect() {
    PID=$(ps -o "pid args" -u $(id -u) | grep "kubectl.*port-forward service/$NAME" | grep -v grep | head -1 | awk '{print $1}')
    ADDRESS=http://$(ss -lpnt | grep pid=$PID, | head -1 | awk '{print $4}')
    echo "firefox $ADDRESS"
    firefox $ADDRESS
}

cd ${0%/*}

NAME=$(grep ^NAME Makefile | awk '{print $NF}')
if [ "$(ps -o "pid args" -u $(id -u) | grep "kubectl.*port-forward service/$NAME" | grep -v grep)" ]
then
    connect
else
    sleep 2 && connect &
    make forward
fi
