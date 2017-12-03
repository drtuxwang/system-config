#!/usr/bin/env wish

. config -bg "#cccccc"

frame .toolbar -bg "#cccccc"
    button .toolbar.gb -width 2 -bg "#ffcc00" -text gb -command {
        set map {gb}
        exec setxkbmap gb
    }
    pack .toolbar.gb -side left

    button .toolbar.de -width 2 -bg "#ffff00" -text de -command {
        set map {de}
        exec setxkbmap de
    }
    pack .toolbar.de -side left

    button .toolbar.us -width 2 -bg "#ffff00" -text us -command {
        set map {us}
        exec setxkbmap us
    }
    pack .toolbar.us -side left

    entry .toolbar.map -width 4 -textvar map
    pack .toolbar.map -side left

    button .toolbar.set -width 3 -bg "#00ff00" -text Set -command {
        exec setxkbmap ${map} &
    }
    pack .toolbar.set -side right
pack .toolbar -side top -fill x

set map {}
