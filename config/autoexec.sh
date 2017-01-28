#!/bin/bash

set_vga()
{
    MODELINE=$(gtf 1440 900 60 | grep Modeline | awk '{
        printf("%4.2f %d %d %d %d %d %d %d %d\n", $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
    }')
    xrandr --newmode $2x${3}_$4 $MODELINE
    xrandr --addmode $1 $2x${3}_$4
    xrandr --dpi 96
    sleep 1
    xrandr -s $2x${3}_$4
}

start_app()
{
    NAME=
    TIMEOUT=10
    while [[ $1 = -* ]]
    do
        case $1 in
        -pname=*)
            NAME=`echo "$1" | cut -f2- -d"="`
            ;;
        -timeout=*)
            TIMEOUT=`echo "$1" | cut -f2- -d"="`
            ;;
        esac
        shift
    done
    if [ ! "$NAME" ]
    then
        NAME=$1
    fi

    echo "Starting \"$@\"..."
    "$@" &
    sleep 4
    for DELAY in $(seq 5 $TIMEOUT)
    do
        sleep 1
        if [ ! "$(ps -o "args" | sed -e "s/^/ /" -e "s/\$/ /" | grep "[ /]$NAME ")" ]
        then
            echo "Restarting \"$1\" after $DELAY seconds..."
            "$@" &
            return
        fi
    done
    echo "Running \"$@\"..."
}


if [ "$1" != "-start" ]
then
    exec $0 -start > ${0%%.sh}.log 2>&1
fi

MYUNAME=`id | sed -e 's/^[^(]*(\([^)]*\)).*$/\1/'`

if [ ! "$BASE_PATH" ]
then
    export BASE_PATH=$PATH
    export BASE_LD_LIBRARY_PATH=$LD_LIBRARY_PATH
    export BASE_LM_LICENSE_FILE=$LM_LICENSE_FILE
    export BASE_PYTHONPATH=$PYTHONPATH
    export BASE_MANPATH=$MANPATH
    export PATH="$HOME/software/bin:/opt/software/bin:$HOME/.local/bin:$PATH"
fi

if [ -x /usr/bin/ibus-daemon ]
then
    export GTK_IM_MODULE=ibus
    export QT_IM_MODULE=ibus
    export XMODIFIERS=@im=ibus
fi

chmod go= $HOME/Desktop data/private .??*/* 2> /dev/null
for HOST in "" `xhost | grep "^INET:"`
do
    xhost -$HOST
done
xhost +si:localuser:$MYUNAME

setxkbmap gb
setxkbmap -option terminate:ctrl_alt_bksp
xset b off
xset m 4,16
xset r rate 500 25
xset s blank s 0 # Use 300 for CRT
(sleep 4 && xset dpms 0 0 0) &

rm -rf $HOME/.thumbnails $HOME/.gnome2/evince/ev-metadata.xml
if [ "$GNOME_DESKTOP_SESSION_ID" -o "`echo \"$DESKTOP_SESSION\" | grep gnome`" ]
then
    gnome-sound-applet &
elif [ -d $HOME/.cache/sessions ]
then
    rm -rf $HOME/.cache/sessions
    touch $HOME/.cache/sessions
fi
for FILE in .recently-used.xbel .local/share/recently-used.xbel
do
    rm -f $FILE 2> /dev/null
    mkdir -p $FILE 2> /dev/null
done

export SSH_AUTH_SOCK=$(ls -1t /tmp/ssh-*/* 2> /dev/null | head -1)
if [ ! "$SSH_AUTH_SOCK" ]
then
    eval $(ssh-agent)
fi
menu

if [ -f $HOME/.config/autoexec-local.sh ]
then
    . $HOME/.config/autoexec-local.sh
fi
