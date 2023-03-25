#!/usr/bin/env bash

# Optional input environment
ARG=${1:-}

export MYUNAME=$(whoami 2> /dev/null)
[ ! "$MYUNAME" ] && MYUNAME=$(id -un)

# Fix logging
[ "$ARG" != "-start" ] && exec $0 -start > $TMP/.cache/autoexec.log 2>&1

# Protect files
chmod 711 $HOME
ls -ld $TMP $HOME/Desktop $HOME/Desktop/private $HOME/.ssh $HOME/.??*/* 2> /dev/null | \
    grep -v "[-]----- " | awk '{print $NF}' | xargs -n 1 chmod go= 2> /dev/null

# Use /tmp (tmpfs) for cache
export TMPDIR=/tmp/$MYUNAME
export TMP=/tmp/$MYUNAME
mkdir -p $TMP/.cache
rm -f $(find $HOME/.???* -xdev -type l | xargs -r -d '\n' ls -ld | \
    grep " -> /tmp" | grep -v " -> /tmp/$MYUNAME/" | sed -e "s/ ->.*//;s/.* //")
[ ! -h $HOME/.cache ] && rm -rf $HOME/.cache && ln -s $TMP/.cache $HOME/.cache
[ ! -h $HOME/.local/share/gvfs-metadata ] && \
    rm -rf $HOME/.local/share/gvfs-metadata && ln -s $TMP/.cache $HOME/.local/share/gvfs-metadata
[ ! -h $HOME/.fontconfig ] && rm -rf $HOME/.fontconfig &&  ln -s $TMP/.cache $HOME/.fontconfig
[ ! -d "$HOME/.local/share/recently-used.xbel" ] && \
    rm -f $HOME/.local/share/recently-used.xbel && mkdir -p $HOME/.local/share/recently-used.xbel
[ ! -h $HOME/.pki ] && rm -rf $HOME/.pki &&  ln -s $TMP/.cache $HOME/.pki
[ ! -d "$HOME/.recently-used.xbel" ] && \
    rm -f $HOME/.recently-used.xbel && mkdir -p $HOME/.recently-used.xbel
[ ! -d $HOME/.xsession-errors.old ] && \
    rm -f $HOME/.xsession-errors.old && mkdir $HOME/.xsession-errors.old
[ ! -h $HOME/.xsession-errors ] && \
    rm -f $HOME/.xsession-errors && ln -s /dev/null $HOME/.xsession-errors
[ ! -d $HOME/.xfce4-session.verbose-log.last ] && \
    rm -f $HOME/.xfce4-session.verbose-log.last && mkdir $HOME/.xfce4-session.verbose-log.last
[ ! -h $HOME/.xfce4-session.verbose-log ] && \
    rm -f $HOME/.xfce4-session.verbose-log && ln -s /dev/null $HOME/.xfce4-session.verbose-log
[ ! -h $HOME/tmp || ! -w $HOME/tmp ] && rm -rf $HOME/tmp && ln -s $TMP $HOME/tmp

# Wipe Trash
rm -rf $HOME/.local/share/Trash/* &

# Save default settings (PATH, MANPATH, LM_LICENSE_FILE, DSOPATH)
if [ ! "$BASE_PATH" ]
then
    export BASE_PATH=$PATH
    export BASE_LD_LIBRARY_PATH=$LD_LIBRARY_PATH
    export BASE_LM_LICENSE_FILE=$LM_LICENSE_FILE
    export BASE_PYTHONPATH=$PYTHONPATH
    export BASE_MANPATH=$MANPATH
    export PATH="$HOME/software/bin:/opt/software/bin:$HOME/.local/bin:$PATH"
fi

# Setup SSH agent
export SSH_AUTH_SOCK=$(ls -1t /tmp/ssh-*/* 2> /dev/null | head -1)
[ ! "$SSH_AUTH_SOCK" ] && eval $(ssh-agent)

# Setup display
for HOST in "" $(xhost | grep "^INET:")
do
    xhost -$HOST
done
xhost +si:localuser:$MYUNAME
xrandr --dpi 96
xset dpms 0 0 0 &
xset s blank s 0 # Use 300 for CRT
export QT_AUTO_SCREEN_SCALE_FACTOR=0

# Setup IBus input
if [ -x /usr/bin/ibus-daemon ]
then
    ibus-daemon --daemonize --replace
    export GTK_IM_MODULE=ibus
    export QT_IM_MODULE=ibus
    export XMODIFIERS=@im=ibus
fi

# Start launcher
menu
sleep 2

# Setup audio
pactl set-sink-volume 0 100%

# Setup mouse
xset m 4,16

# Setup keyboard
setxkbmap gb
setxkbmap -option ctrl:nocaps              # Disable Caps Lock
setxkbmap -option altwin:ctrl_win          # Map Win key to Ctrl (like Mac)
setxkbmap -option terminate:ctrl_alt_bksp  # Zap with Ctrl+Alt+BackSpace
xmodmap -e "add mod3 = Scroll_Lock" &
xset b off
xset r rate 500 25
numlockx off
[ "$(ls /dev/input/by-path/*usb*kbd 2> /dev/null)" ] && numlockx on && xmodmap -e "keycode 77 = NoSymbol" &

# Optional setup
[ -f $HOME/.config/autoexec-opt.sh ] && . $HOME/.config/autoexec-opt.sh
