#!/usr/bin/env wish

. config -bg "#cccccc"


frame .top -bg "#cccccc"
    entry .top.hostname -width 13 -relief sunken -textvariable hostname
    pack .top.hostname -side left
pack .top -fill x

frame .middle -bg "#cccccc"
    entry .middle.xsize -width 4 -relief sunken -textvariable xsize
    pack .middle.xsize -side left
    pack .middle -side top -fill x
    button .middle.reset -width 1 -bg "#ffff00" -text "X" -command { set xsize {1280}; set ysize {960} }
    pack .middle.reset -side left
    entry .middle.ysize -width 4 -relief sunken -textvariable ysize
    pack .middle.ysize -side left
pack .middle -fill x

frame .bottom -bg "#cccccc"
    button .bottom.connect -width 10 -bg "#00ff00" -text "Connect" -command {exec rdesktop -d "" -u "" -g ${xsize}x$ysize -a 24 ${hostname} &}
    pack .bottom.connect -side top
pack .bottom -side top -fill x

set hostname {hostname.local}
set xsize {1280}
set ysize {960}
