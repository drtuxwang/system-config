#!/usr/bin/env bash

# Optional input environment
ARG=${1:-}

# Fix logging
[ "$ARG" != "-start" ] && mkdir -p /tmp/$(id -un) && exec $0 -start > /tmp/$(id -un)/.autostart.log 2>&1

# Setup bash
export TERM=xterm
source $HOME/.profile
[ ! "$BASE_PATH" ] && export BASE_PATH="$PATH"
export PATH="$HOME/software/scripts:$HOME/software/bin:/opt/software/bin:$BASE_PATH"
export TMPDIR=${TMPDIR:-/tmp/$(id -un)}

# Use /tmp (tmpfs) for cache
[ ! -h $HOME/.local/share/gvfs-metadata ] && rm -rf $HOME/.local/share/gvfs-metadata && ln -s $TMPDIR/.cache $HOME/.local/share/gvfs-metadata
[ ! -h $HOME/.fontconfig ] && rm -rf $HOME/.fontconfig &&  ln -s $TMPDIR/.cache $HOME/.fontconfig
[ ! -d "$HOME/.local/share/recently-used.xbel" ] && rm -f $HOME/.local/share/recently-used.xbel && mkdir -p $HOME/.local/share/recently-used.xbel
[ ! -h $HOME/.pki ] && rm -rf $HOME/.pki &&  ln -s $TMPDIR/.cache $HOME/.pki
[ ! -d "$HOME/.recently-used.xbel" ] && rm -f $HOME/.recently-used.xbel && mkdir -p $HOME/.recently-used.xbel
[ ! -d $HOME/.xsession-errors.old ] && rm -f $HOME/.xsession-errors.old && mkdir $HOME/.xsession-errors.old
[ ! -h $HOME/.xsession-errors ] && rm -f $HOME/.xsession-errors && ln -s /dev/null $HOME/.xsession-errors
[ ! -h $HOME/Desktop/tmp ] && rm -rf $HOME/Desktop/tmp && ln -s $TMPDIR $HOME/Desktop/tmp

# Wipe Trash
rm -rf $HOME/.local/share/Trash/* &

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
    ibus-daemon --daemonize --xim --replace
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
[ -f $HOME/.config/autostart-opt.bash ] && . $HOME/.config/autostart-opt.bash
