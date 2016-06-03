#!/bin/sh

if [ "`lspci 2> /dev/null | grep VirtualBox`" ]; then
    # xrandr --newmode "1280x960" 102.10 1280 1360 1496 1712 960 961 964 994 # gtf 1280 960 60
    # xrandr --addmode VGA-0 1280x960
    (sleep 1; xrandr --dpi 96; sleep 1; xrandr -s 1024x768) &
fi

# setxkbmap us  # "gb", "de", "us"
# xset m 2,16  # Slow mouse

# xreset
# firefox
# chrome
