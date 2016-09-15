#!/bin/sh

if [ "$1" != "-start" ]; then
    exec $0 -start > ${0%%.sh}.log 2>&1
fi

MYUNAME=`id | sed -e 's/^[^(]*(\([^)]*\)).*$/\1/'`
BASE_PATH=$PATH; export BASE_PATH
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
