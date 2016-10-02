#!/bin/sh

set_vbox()
{
    sleep 1
    xrandr --dpi 96
    sleep 1
    xrandr -s 1024x768
}

set_vga()
{
    MODELINE=$(gtf 1440 900 60 | grep Modeline | awk '{
        printf("%4.2f %d %d %d %d %d %d %d %d\n", $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
    }')
    echo xrandr --newmode $2x${3}_$4 $MODELINE
    echo xrandr --addmode $1 $2x${3}_$4
    echo xrandr -s $2x$3
}

start_app()
{
    echo "Starting \"$@\"..."
    "$@" &
    for _ in `seq 15`; do
        sleep 1
        if [ ! "$(ps -o "pid args " | grep "[ /]$1 ")" ]; then
            echo "Restarting \"$1\"..."
            "$@" &
            break
        fi
    done
}


if [ "$1" != "-start" ]; then
    exec $0 -start > ${0%%.sh}.log 2>&1
fi

MYUNAME=`id | sed -e 's/^[^(]*(\([^)]*\)).*$/\1/'`

BASE_PATH=$PATH; export BASE_PATH
BASE_MANPATH=$MANPATH; export MANPATH
BASE_LM_LICENSE_FILE=$LM_LICENSE_FILE; export LM_LICENSE_FILE
BASE_LD_LIBRARY_PATH=$LD_LIBRARY_PATH; export LD_LIBRARY_PATH
PATH="$HOME/software/bin:/opt/software/bin:$HOME/.local/bin:$PATH"; export PATH

if [ -x /usr/bin/ibus-daemon ]; then
    GTK_IM_MODULE=ibus; export GTK_IM_MODULE
    QT_IM_MODULE=ibus; export QT_IM_MODULE
    XMODIFIERS=@im=ibus; export XMODIFIERS
fi

chmod go= $HOME/Desktop data/private .??*/* 2> /dev/null
for HOST in "" `xhost | grep "^INET:"`; do
    xhost -$HOST
done
xhost +si:localuser:$MYUNAME

setxkbmap gb
setxkbmap -option terminate:ctrl_alt_bksp
xset b off
xset m 4,16
xset r rate 500 25
xset s blank s 0 # Use 300 for CRT
(sleep 4; xset dpms 0 0 0) &

rm -rf $HOME/.thumbnails $HOME/.gnome2/evince/ev-metadata.xml
if [ "$GNOME_DESKTOP_SESSION_ID" -o "`echo \"$DESKTOP_SESSION\" | grep gnome`" ]; then
    gnome-sound-applet &
elif [ -d $HOME/.cache/sessions ]; then
    rm -rf $HOME/.cache/sessions; touch $HOME/.cache/sessions
fi
for FILE in .recently-used.xbel .local/share/recently-used.xbel; do
    rm -f $FILE 2> /dev/null
    mkdir -p $FILE 2> /dev/null
done

eval `/usr/bin/gnome-keyring-daemon --start --components=pkcs11,secrets,ssh,gpg` 2> /dev/null
menu

if [ -f $HOME/.config/autoexec-local.sh ]; then
    . $HOME/.config/autoexec-local.sh
fi
