#!/bin/bash

# Optional input environment
ARG=${1:-}

MYUNAME=`id | sed -e 's/^[^(]*(\([^)]*\)).*$/\1/'`

# Use /tmp (tmpfs) for cache
export TMPDIR=/tmp/$MYUNAME
export TMP=/tmp/$MYUNAME
mkdir -p $TMP/.cache
ls -ld $TMP $HOME/Desktop $HOME/Desktop/private $HOME/.ssh $HOME/.??*/* 2> /dev/null | \
    grep -v "[-]----- " | awk '{print $NF}' | xargs -n 1 chmod go= 2> /dev/null

# Fix logging
[[ "$ARG" != "-start" ]] && exec $0 -start > $TMP/.cache/autoexec.log 2>&1

# Secure cache/logs
[[ ! -h $HOME/.cache ]] && rm -rf $HOME/.cache && ln -s $TMP/.cache $HOME/.cache
[[ ! -h $HOME/.local/share/gvfs-metadata ]] && rm -rf $HOME/.local/share/gvfs-metadata && ln -s $TMP/.cache $HOME/.local/share/gvfs-metadata
[[ ! -h $HOME/.fontconfig ]] && rm -rf $HOME/.fontconfig &&  ln -s $TMP/.cache $HOME/.fontconfig
[[ ! -d "$HOME/.local/share/recently-used.xbel" ]] && rm -f $HOME/.local/share/recently-used.xbel && mkdir -p $HOME/.local/share/recently-used.xbel
[[ ! -h $HOME/.pki ]] && rm -rf $HOME/.pki &&  ln -s $TMP/.cache $HOME/.pki
[[ ! -d "$HOME/.recently-used.xbel" ]] && rm -f $HOME/.recently-used.xbel && mkdir -p $HOME/.recently-used.xbel
[[ ! -h $HOME/tmp ]] && rm -rf $HOME/tmp &&  ln -s $TMP $HOME/tmp
[[ ! -d $HOME/.xsession-errors.old ]] && rm -f $HOME/.xsession-errors.old && mkdir $HOME/.xsession-errors.old
[[ ! -h $HOME/.xsession-errors ]] && rm -f $HOME/.xsession-errors && ln -s /dev/null $HOME/.xsession-errors
[[ ! -d $HOME/.xfce4-session.verbose-log.last ]] && rm -f $HOME/.xfce4-session.verbose-log.last && mkdir $HOME/.xfce4-session.verbose-log.last
[[ ! -h $HOME/.xfce4-session.verbose-log ]] && rm -f $HOME/.xfce4-session.verbose-log && ln -s /dev/null $HOME/.xfce4-session.verbose-log

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
xset b off
xset m 4,16
xset r rate 500 25
xset s blank s 0 # Use 300 for CRT
if [ "$(ls /dev/input/by-path/*usb*kbd 2> /dev/null)" ]
then
    sleep 2 && numlockx on && xmodmap -e "keycode 77 = NoSymbol" &
else
    sleep 2 && numlockx off &
fi
sleep 2 && xmodmap -e "add mod3 = Scroll_Lock" &
sleep 4 && xset dpms 0 0 0 &

rm -rf $HOME/.thumbnails $HOME/.gnome2/evince/ev-metadata.xml

export SSH_AUTH_SOCK=$(ls -1t /tmp/ssh-*/* 2> /dev/null | head -1)
[[ ! "$SSH_AUTH_SOCK" ]] && eval $(ssh-agent)
menu

[[ -f $HOME/.config/autoexec-opt.sh ]] && . $HOME/.config/autoexec-opt.sh
