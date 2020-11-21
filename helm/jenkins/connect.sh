#!/bin/bash

connect() {
    for _ in {1..10}
    do
        PID=$(ps -o "pid args" -u $(id -u) | grep "kubectl.*port-forward service/$NAME" | grep -v grep | awk 'NR==1 {print $1}')
        ADDRESS=$(ss -lpnt | grep pid=$PID, | awk 'NR==1 {print $4}')
        if [ "$ADDRESS" ]
        then
            echo "firefox http://$ADDRESS"
            firefox http://$ADDRESS
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
