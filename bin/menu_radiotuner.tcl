#!/usr/bin/env wish

. config -bg "#cccccc"

frame .english -bg "#cccccc"
    button .english.magic -width 10 -bg "#ffcc00" -text "Magic 105.4" -command {
        exec xweb http://magic1054.radio.net/ &
    }
    pack .english.magic -side top
pack .english -side top -fill x

frame .chinese -bg "#cccccc"
    button .chinese.988 -width 10 -bg "#ffff00" -text "988最好听" -command {
        exec xweb http://listen.988.com.my/ &
    }
    pack .chinese.988 -side top

    button .chinese.rthk1 -width 10 -bg "#ffff00" -text "RTHK 1" -command {
        exec xweb http://www.rthk.hk/radio/radio1/ &
    }
    pack .chinese.rthk1 -side top

    button .chinese.rthk2 -width 10 -bg "#ffff00" -text "RTHK 2" -command {
        exec xweb http://www.rthk.hk/radio/radio2/ &
    }
    pack .chinese.rthk2 -side top

    button .chinese.rthk3 -width 10 -bg "#ffff00" -text "RTHK 3" -command {
        exec xweb http://www.rthk.hk/radio/radio3/ &
    }
    pack .chinese.rthk3 -side top

    button .chinese.rthk4 -width 10 -bg "#ffff00" -text "RTHK 4" -command {
        exec xweb http://www.rthk.hk/radio/radio4/ &
    }
    pack .chinese.rthk4 -side top

    button .chinese.rthk5 -width 10 -bg "#ffff00" -text "RTHK 5" -command {
        exec xweb http://www.rthk.hk/radio/radio5/ &
    }
    pack .chinese.rthk5 -side top

    button .chinese.rthkpth -width 10 -bg "#ffff00" -text "RTHK普通話" -command {
        exec xweb http://www.rthk.hk/radio/pth/ &
    }
    pack .chinese.rthkpth -side top
pack .chinese -side top -fill x

frame .menu -bg "#cccccc"
    button .menu.close -width 10 -bg "#ff0000" -text Close -command exit
    pack .menu.close -side top
pack .menu -side top -fill x
