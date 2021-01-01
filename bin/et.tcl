#!/usr/bin/env wish

wm resizable . 0 0
wm title . "ET"
wm geometry . +0+0

. config -bg "#cccccc"


frame .menu -bg "#cccccc"

    button .menu.etwolf -width 10 -bg "#ffcc00" -text "ET" -command {
        exec et &
    }
    pack .menu.etwolf -side top

    button .menu.bba_jay -width 10 -bg "#ffff00" -text "BBA(Jay)" -command {
        exec et +connect 173.230.141.36:27960 &
    }
    pack .menu.bba_jay -side top
    button .menu.fa_b1 -width 10 -bg "#ffff00" -text "FA(B1)" -command {
        exec et +connect b1.clan-fa.com:27960 &
    }
    pack .menu.fa_b1 -side top
    button .menu.fa_b2 -width 10 -bg "#ffff00" -text "FA(B2)" -command {
        exec et +connect b2.clan-fa.com:27960 &
    }
    pack .menu.fa_b2 -side top
    button .menu.etc_nit -width 10 -bg "#ffff00" -text "Etc(Nit)" -command {
        exec et +connect 185.248.141.23:27960 &
    }
    pack .menu.etc_nit -side top

    button .menu.close -width 10 -bg "#ff0000" -text "Close" -command {
        exit
    }
    pack .menu.close -side top

pack .menu -side top -fill x
