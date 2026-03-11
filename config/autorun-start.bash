#!/usr/bin/env bash

# Optional input environment
ARG=${1:-}

# Fix logging
[ "$ARG" != "-start" ] && mkdir -p /tmp/$(id -un) && exec $0 -start > /tmp/$(id -un)/.autorun-start.log 2>&1

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

# Setip pipewire aduio volume
wpctl set-volume @DEFAULT_AUDIO_SINK@ 1.0

# Setup mouse
xset m 4,16
# Setup keyboard
while [ ! "$(setxkbmap -query | grep ctrl:nocaps,altwin:ctrl_win,terminate:ctrl_alt_bksp)" ]
do
   setxkbmap gb
   # Disable CapsLock, Win key as Ctrl (like Mac), Ctrl+Alt+BackSpace
   setxkbmap -option -option ctrl:nocaps,altwin:ctrl_win,terminate:ctrl_alt_bksp
   xmodmap -e "add mod3 = Scroll_Lock" &
   xset b off
   xset r rate 500 25
   numlockx off
    [ "$(ls /dev/input/by-path/*usb*kbd 2> /dev/null)" ] && numlockx on && xmodmap -e "keycode 77 = NoSymbol" &
   sleep 1
done

# Optional setup
[ -f $HOME/.config/autorun-start-opt.bash ] && . $HOME/.config/autorun-start-opt.bash
