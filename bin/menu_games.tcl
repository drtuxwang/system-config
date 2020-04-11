#!/usr/bin/env wish

. config -bg "#cccccc"

frame .small -bg "#cccccc"
    button .small.chess -width 10 -bg "#ffcc00" -text "Dream Chess" -command {
        exec dreamchess &
    }
    pack .small.chess -side top

    button .small.frozenbubble -width 10 -bg "#ffcc00" -text "Frozen Bubble" -command {
        exec frozen-bubble &
    }
    pack .small.frozenbubble -side top

    button .small.hearts -width 10 -bg "#ffcc00" -text "Hearts" -command {
        exec gnome-hearts &
    }
    pack .small.hearts -side top

    button .small.mines -width 10 -bg "#ffcc00" -text "Mines" -command {
       exec gnomine &
    }
    pack .small.mines -side top

    button .small.neverputt -width 10 -bg "#ffcc00" -text "Neverputt" -command {
       exec neverputt &
    }
    pack .small.neverputt -side top

    button .small.reversi -width 10 -bg "#ffcc00" -text "Iagno" -command {
        exec iagno &
    }
    pack .small.reversi -side top

    button .small.sudoku -width 10 -bg "#ffcc00" -text "Sudoku" -command {
        exec gnome-sudoku &
    }
    pack .small.sudoku -side top

    button .small.swellfoop -width 10 -bg "#ffcc00" -text "Swell Foop" -command {
        exec swell-foop &
    }
    pack .small.swellfoop -side top
pack .small -side top -fill x

frame .large -bg "#cccccc"
    button .large.0ad -width 10 -bg "#ffff00" -text "0AD" -command {
        exec 0ad &
    }
    pack .large.0ad -side top

    button .large.assaultcube -width 10 -bg "#ffff00" -text "AssaultCube" -command {
        exec assaultcube &
    }
    pack .large.assaultcube -side top

    button .large.et -width 10 -bg "#ffff00" -text "ET" -command {
        exec et &
    }
    pack .large.et -side top

    button .large.freecol -width 10 -bg "#ffff00" -text "Freecol" -command {
        exec freecol &
    }
    pack .large.freecol -side top

    button .large.et_bba -width 10 -bg "#ffff00" -text "ET:BBA" -command {
        exec et +connect 173.230.141.36:27960 &
    }
    pack .large.et_bba -side top

    button .large.et_etc -width 10 -bg "#ffff00" -text "ET:Etc" -command {
        exec et +connect 185.248.141.23:27960 &
    }
    pack .large.et_etc -side top

    button .large.et_ets -width 10 -bg "#ffff00" -text "ET:Ets" -command {
        exec et +connect 104.243.41.34:27960 &
    }
    pack .large.et_ets -side top

    button .large.tuxracer -width 10 -bg "#ffff00" -text "Tux Racer" -command {
        exec etr &
    }
    pack .large.tuxracer -side top

    button .large.wesnoth -width 10 -bg "#ffff00" -text "Wesnoth" -command {
        exec wesnoth &
    }
    pack .large.wesnoth -side top
pack .large -side top -fill x

frame .menu -bg "#cccccc"
    button .menu.close -width 10 -bg "#ff0000" -text Close -command exit
    pack .menu.close -side top
pack .menu -side top -fill x
