#!/bin/bash

# Optional input environment
ARG=${1:-}

MYUNAME=`id | sed -e 's/^[^(]*(\([^)]*\)).*$/\1/'`

# Use /tmp (tmpfs) for cache
mkdir -p /tmp/$MYUNAME/.cache 2> /dev/null
chmod 700 /tmp/$MYUNAME
export TMP=/tmp/$MYUNAME
export TMPDIR=$TMP

# Enable logging
if [ "$ARG" != "-start" ]
then
    exec $0 -start > $TMP/.cache/autoexec.log 2>&1
fi

# Secure temp files
[[ ! -h $HOME/tmp ]] && rm -rf $HOME/tmp &&  ln -s $TMP $HOME/tmp
[[ ! -h $HOME/.cache ]] && rm -rf $HOME/.cache && ln -s $TMP/.cache $HOME/.cache
[[ ! -h $HOME/.local/share/gvfs-metadata ]] && rm -rf $HOME/.local/share/gvfs-metadata && ln -s $TMP/.cache $HOME/.local/share/gvfs-metadata
for FILE in .recently-used.xbel .local/share/recently-used.xbel
do
    [[ -f "$HOME/$FILE" ]] && rm -f $HOME/$FILE 2> /dev/null && mkdir -p $HOME/$FILE 2> /dev/null
done

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
setxkbmap -option ctrl:nocaps
setxkbmap -option terminate:ctrl_alt_bksp
(sleep 2; numlockx on && xmodmap -e "keycode 77 = NoSymbol") &
xset b off
xset m 4,16
xset r rate 500 25
xset s blank s 0 # Use 300 for CRT
(sleep 4 && xset dpms 0 0 0) &

rm -rf $HOME/.thumbnails $HOME/.gnome2/evince/ev-metadata.xml
if [ "$GNOME_DESKTOP_SESSION_ID" -o "`echo \"$DESKTOP_SESSION\" | grep gnome`" ]
then
    gnome-sound-applet &
fi

export SSH_AUTH_SOCK=$(ls -1t /tmp/ssh-*/* 2> /dev/null | head -1)
if [ ! "$SSH_AUTH_SOCK" ]
then
    eval $(ssh-agent)
fi
menu

if [ -f $HOME/.config/autoexec-opt.sh ]
then
    . $HOME/.config/autoexec-opt.sh
fi
