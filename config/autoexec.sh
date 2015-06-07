#!/bin/sh

MYUNAME=`id | sed -e 's/^[^(]*(\([^)]*\)).*$/\1/'`
PATH=$HOME/software/bin:$PATH; export PATH

if [ "`lsmod | grep vboxvideo`" ]; then
    (xrandr --dpi 96; sleep 1; xrandr -s 1280x960) &
fi

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

(sleep 1; menu) &

setxkbmap gb
setxkbmap -option terminate:ctrl_alt_bksp
xset m 4,8
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
myqsd 1

if [ -f $HOME/.config/autoexec-local.sh ]; then
    . $HOME/.config/autoexec-local.sh
fi
