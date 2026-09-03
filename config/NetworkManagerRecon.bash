#!/usr/bin/env bash
#
# NetworkManger does not support IPv6 prefix change by router
# This service reconnect device when routing problem detected
#

ip -6 monitor address | while read LINE
do
    case $LINE in
    *global\ dynamic\ mngtmpaddr*)
        DEVICE=$(echo "$LINE" | sed -e "s/^[^:]*: //;s/ .*//")
        IPS=$(ip addr show dev $DEVICE | grep "global dynamic mngtmpaddr")
        if [ $(echo "$IPS" | wc -l) -gt 1 ]
        then
            CONNECTION=$(nmcli -f DEVICE,UUID connection | grep "^$DEVICE " | awk '{print $2}')
            echo "$IPS" | sed -e "s/^ */$DEVICE: /"
            echo "nmcli connection down $CONNECTION && nmcli connection up $CONNECTION"
            nmcli connection down $CONNECTION && nmcli connection up $CONNECTION
        fi
        ;;
    esac
done

