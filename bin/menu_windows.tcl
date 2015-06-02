#!/usr/bin/env wish

. config -bg "#cccccc"


# Rdesktop size
frame .input -bg "#cccccc"

    entry .input.xsize -width 4 -relief sunken -textvariable xsize

    pack .input.xsize -side left
    pack .input -side top -fill x

    button .input.reset -width 1 -bg "#00ff00" -text "X" -command { set xsize {1280}; set ysize {960} }
    pack .input.reset -side left

    entry .input.ysize -width 4 -relief sunken -textvariable ysize
    pack .input.ysize -side left

pack .input -fill x


frame .mainmenu -bg "#cccccc"

# Windows_x86_64
    button .mainmenu.winxp -width 10 -bg "#ffff00" -text "winxp" -command {exec rdesktop -d windows -u "" -g ${xsize}x$ysize -a 24 winxp &}
    pack .mainmenu.winxp -side top

pack .mainmenu -side top -fill x


set xsize {1280}
set ysize {960}

