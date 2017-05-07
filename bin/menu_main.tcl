#!/usr/bin/env wish

. config -bg "#cccccc"

frame .shell -bg "#cccccc"
    button .shell.console -width 10 -bg "#ffcc00" -text Console -command {
        exec xterm &
    }
    pack .shell.console -side top

    button .shell.desktop -width 10 -bg "#ffcc00" -text Desktop -command {
        exec xdesktop Desktop &
    }
    pack .shell.desktop -side top

    button .shell.browser -width 10 -bg "#ffff00" -text "Browser" -command {
         exec chromium &
    }
    pack .shell.browser -side top
pack .shell -side top -fill x

frame .submenu -bg "#cccccc"
    button .submenu.document -width 10 -bg "#00ff00" -text "Document" -command {
        exec menu_document.tcl &
    }
    pack .submenu.document -side top

    button .submenu.games -width 10 -bg "#00ff00" -text "Games" -command {
        exec menu_games.tcl &
    }
    pack .submenu.games -side top

    button .submenu.graphics -width 10 -bg "#00ff00" -text "Graphics" -command {
        exec menu_graphics.tcl &
    }
    pack .submenu.graphics -side top

    button .submenu.multimedia -width 10 -bg "#00ff00" -text "Multimedia" -command {
        exec menu_multimedia.tcl &
    }
    pack .submenu.multimedia -side top

    button .submenu.network -width 10 -bg "#00ff00" -text "Network" -command {
        exec menu_network.tcl &
    }
    pack .submenu.network -side top

    button .submenu.system -width 10 -bg "#00ff00" -text "System" -command {
        exec menu_system.tcl &
    }
    pack .submenu.system -side top

    button .submenu.utility -width 10 -bg "#00ff00" -text "Utility" -command {
        exec menu_utility.tcl &
    }
    pack .submenu.utility -side top
pack .submenu -side top -fill x

frame .menu -bg "#cccccc"
    button .menu.lock -width 10 -bg "#ff0000" -text "Lock Screen" -command {
        exec xlock &
    }
    pack .menu.lock -side top
pack .menu -side top -fill x
