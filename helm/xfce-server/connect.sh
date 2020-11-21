#!/bin/bash

connect() {
    for _ in {1..10}
    do
        PID=$(ps -o "pid args" -u $(id -u) | grep "kubectl.*port-forward service/$NAME" | grep -v grep | awk 'NR==1 {print $1}')
        LOCALPORT=$(ss -lpnt | grep pid=$PID, | awk 'NR==1 {print $4}' | sed -e "s/.*://")
        if [ "$LOCALPORT" ]
        then
            echo "svncviewer -p $LOCALPORT owner@localhost:5901"
            svncviewer -p $LOCALPORT owner@localhost:5901
            return
        fi
        sleep 1
    done
    echo "Failed!"
}

cd ${0%/*}

NAME=$(grep ^NAME Makefile | awk '{print $NF}')
if [ "$(ps -o "pid args" -u $(id -u) | grep "kubectl.*port-forward service/$NAME" | grep -v grep)" ]
then
    connect
else
    connect &
    make forward
fi
