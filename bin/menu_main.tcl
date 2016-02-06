#!/usr/bin/env wish

. config -bg "#cccccc"


frame .mainmenu -bg "#cccccc"

    button .mainmenu.console -width 10 -bg "#ffcc00" -text Console -command {exec xterm &}
    pack .mainmenu.console -side top
    button .mainmenu.desktop -width 10 -bg "#ffcc00" -text Desktop -command {exec xdesktop Desktop &}
    pack .mainmenu.desktop -side top
    button .mainmenu.chrome -width 10 -bg "#ffff00" -text "Chrome" -command {exec chrome &}
    pack .mainmenu.chrome -side top
    button .mainmenu.firefox -width 10 -bg "#ffff00" -text "Firefox" -command {exec firefox &}
    pack .mainmenu.firefox -side top

# Menus
    button .mainmenu.menu_document -width 10 -bg "#00ff00" -text "Document" -command {exec menu_document.tcl &}
    pack .mainmenu.menu_document -side top
    button .mainmenu.menu_games -width 10 -bg "#00ff00" -text "Games" -command {exec menu_games.tcl &}
    pack .mainmenu.menu_games -side top
    button .mainmenu.menu_graphics -width 10 -bg "#00ff00" -text "Graphics" -command {exec menu_graphics.tcl &}
    pack .mainmenu.menu_graphics -side top
    button .mainmenu.menu_multimedia -width 10 -bg "#00ff00" -text "Multimedia" -command {exec menu_multimedia.tcl &}
    pack .mainmenu.menu_multimedia -side top
    button .mainmenu.menu_network -width 10 -bg "#00ff00" -text "Network" -command {exec menu_network.tcl &}
    pack .mainmenu.menu_network -side top
    button .mainmenu.menu_system -width 10 -bg "#00ff00" -text "System" -command {exec menu_system.tcl &}
    pack .mainmenu.menu_system -side top
    button .mainmenu.menu_utility -width 10 -bg "#00ff00" -text "Utility" -command {exec menu_utility.tcl &}
    pack .mainmenu.menu_utility -side top

    button .mainmenu.xlock -width 10 -bg "#ff0000" -text "Lock Screen" -command {exec xlock &}
    pack .mainmenu.xlock -side top

pack .mainmenu -side top -fill x
