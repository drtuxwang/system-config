#!/usr/bin/env wish

. config -bg "#cccccc"


frame .mainmenu -bg "#cccccc"

# Standard games
    button .mainmenu.chess -width 10 -bg "#ffcc00" -text "Dream Chess" -command {exec dreamchess &}
    pack .mainmenu.chess -side top
    button .mainmenu.frozenbubble -width 10 -bg "#ffcc00" -text "Frozen Bubble" -command {exec frozen-bubble &}
    pack .mainmenu.frozenbubble -side top
    button .mainmenu.hearts -width 10 -bg "#ffcc00" -text "Hearts" -command {exec gnome-hearts &}
    pack .mainmenu.hearts -side top
    button .mainmenu.mines -width 10 -bg "#ffcc00" -text "Mines" -command {exec gnome-mines &}
    pack .mainmenu.mines -side top
    button .mainmenu.reversi -width 10 -bg "#ffcc00" -text "Iagno" -command {exec iagno &}
    pack .mainmenu.reversi -side top
    button .mainmenu.sudoku -width 10 -bg "#ffcc00" -text "Sudoku" -command {exec gnome-sudoku &}
    pack .mainmenu.sudoku -side top
    button .mainmenu.swellfoop -width 10 -bg "#ffcc00" -text "Swell Foop" -command {exec swell-foop &}
    pack .mainmenu.swellfoop -side top

# 3D games
    button .mainmenu.0ad -width 10 -bg "#ffff00" -text "0AD" -command {exec 0ad &}
    pack .mainmenu.0ad -side top
    button .mainmenu.assaultcube -width 10 -bg "#ffff00" -text "AssaultCube" -command {exec xrun assaultcube &}
    pack .mainmenu.assaultcube -side top
    button .mainmenu.et -width 10 -bg "#ffff00" -text "ET" -command {exec et &}
    pack .mainmenu.et -side top
    button .mainmenu.et_goc -width 10 -bg "#ffff00" -text "ET:GOC" -command {exec et +connect 213.108.30.108:27960 &}
    pack .mainmenu.et_goc -side top
    button .mainmenu.tuxracer -width 10 -bg "#ffff00" -text "Tux Racer" -command {exec xrun etracer &}
    pack .mainmenu.tuxracer -side top
    button .mainmenu.wesnoth -width 10 -bg "#ffff00" -text "Wesnoth" -command {exec wesnoth &}
    pack .mainmenu.wesnoth -side top

    button .mainmenu.close -width 10 -bg "#ff0000" -text Close -command exit
    pack .mainmenu.close -side top

pack .mainmenu -side top -fill x
