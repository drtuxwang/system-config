#!/usr/bin/env bash
#
# Connect to ingress/service via http/mongodb/oradb/svnc port
#

set -u

MONGODB_CLIENT="robo3t"
ORADB_CLIENT="${0%/*/*/*}../../bin/sqlplus"
CQL_CLIENT="cqlsh"
SVNC_CLIENT="${0%/*/*/*}../../bin/svncviewer"
WEB_CLIENT="firefox"


connect() {
    case $PROTOCOL in
    http|https)
        echo "$WEB_CLIENT $PROTOCOL://$ADDRESS:$PORT"
        $WEB_CLIENT $PROTOCOL://$ADDRESS:$PORT
        ;;
    mongodb)
        echo "Address: $ADDRESS:$PORT"
        curl $ADDRESS:$PORT
        $MONGODB_CLIENT
        ;;
    oradb)
        echo "sqlplus system/oracle@$ADDRESS:$PORT"
        sqlplus system/oracle@$ADDRESS:$PORT
        ;;
    svnc)
        echo "svncviewer -p $PORT $MYUNAME@localhost:5901"
        svncviewer -p $PORT $MYUNAME@localhost:5901
        ;;
    esac
    sleep 1
}


wait_connect() {
    for _ in {1..10}
    do
        sleep 1
        PID=$(ps -o "pid args" -u $(id -u) | grep "$FORWARD" | grep -v grep | awk 'NR==1 {print $1}')
        ADDRESS_PORT=$(ss -lpnt | grep pid=$PID, | awk 'NR==1 {print $4}')
        if [ "$ADDRESS_PORT" ]
        then
            ADDRESS=${ADDRESS_PORT%:*}
            PORT=${ADDRESS_PORT#*:}
            connect
            return
        fi
    done
    echo "Failed!"
}


port_forward() {
    echo "kubectl --namespace=$NAMESPACE port-forward $SERVICE :$PORT"
    kubectl --namespace=$NAMESPACE port-forward $SERVICE :$PORT
}


if [ $# != 1 ]
then
    echo "Usage: $0 protool://address[:port]"
    echo
    echo "arguments:"
    echo "       protocol is http/https/mongodb/oradb/svnc"
    echo "       address is host.subdomain.domain or namespace/service/name:port"
    exit 1
fi

echo "$0 $1"
PROTOCOL=${1%://*}
ADDRESS=$(echo "$1" | sed -e "s@.*://@@;s/:.*//")
PORT=$(echo "$1:80" | cut -f3 -d:)
case $PROTOCOL in
cql|http|https|mongodb|oradb|svnc)
    if [[ $ADDRESS = */service/* ]]
    then
        NAMESPACE=${ADDRESS%%/*}
        SERVICE=${ADDRESS#*/}
        FORWARD="kubectl.*--namespace=$NAMESPACE.*port-forward.*$SERVICE :$PORT"
        [ ! "$(ps -o "pid args" -u $(id -u) | grep "$FORWARD" | grep -v grep)" ] && port_forward &
        wait_connect
    else
        connect
    fi
    ;;
*)
    echo "$0: Unsupported protocol \"$1\""
    exit 1
    ;;
esac
