#!/bin/sh

# Fix VirtualBox resolution to 1280x960
if [ "`lsmod | grep vboxguest`" ]; then
    xrandr --newmode "1280x960" 102.10 1280 1360 1496 1712 960 961 964 994 # gtf 1280 960 60
    xrandr --addmode VGA-0 1280x960
    (xrandr --dpi 96; sleep 1; xrandr -s 1280x960) &
fi

# Slow down mouse
#xset m 2,16

#firefox
#chrome
