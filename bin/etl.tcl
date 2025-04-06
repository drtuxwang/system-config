#!/usr/bin/env wish

wm resizable . 0 0
wm title . "ETL"
wm geometry . +0+0

. config -bg "#cccccc"


frame .menu -bg "#cccccc"

    button .menu.etl32 -width 10 -bg "#ffcc00" -text "ETL(32)" -command {
        exec etl -32 &
    }
    pack .menu.etl32 -side top

    button .menu.etl64 -width 10 -bg "#ffcc00" -text "ETL(64)" -command {
        exec etl &
    }
    pack .menu.etl64 -side top

    button .menu.bba_jay -width 10 -bg "#ffff00" -text "BBA(Jay)" -command {
        exec etl -32 +connect 173.230.141.36:27960 &
    }
    pack .menu.bba_jay -side top
    button .menu.fa_b1 -width 10 -bg "#ffff00" -text "FA(B1)" -command {
        exec etl -32 +connect b1.clan-fa.com:27960 &
    }
    pack .menu.fa_b1 -side top
    button .menu.fa_b2 -width 10 -bg "#ffff00" -text "FA(B2)" -command {
        exec etl -32 +connect b2.clan-fa.com:27960 &
    }
    pack .menu.fa_b2 -side top
    button .menu.etc_nit -width 10 -bg "#ffff00" -text "Etc(Nit)" -command {
        exec etl -32 +connect 84.200.135.3:27980 &
    }
    pack .menu.etc_nit -side top

    button .menu.close -width 10 -bg "#ff0000" -text "Close" -command {
        exit
    }
    pack .menu.close -side top

pack .menu -side top -fill x
