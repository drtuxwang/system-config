#!/bin/bash

connect() {
    PID=$(ps -o "pid args" -u $(id -u) | grep "kubectl.*port-forward service/$NAME" | grep -v grep | head -1 | awk '{print $1}')
    LOCALPORT=$(ss -lpnt | grep pid=$PID, | head -1 | awk '{print $4}' | sed -e "s/.*://")
    echo "svncviewer -p $LOCALPORT owner@localhost:5901"
    svncviewer -p $LOCALPORT owner@localhost:5901
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
