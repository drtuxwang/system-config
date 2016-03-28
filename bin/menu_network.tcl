#!/usr/bin/env wish

. config -bg "#cccccc"


frame .mainmenu -bg "#cccccc"

# Browsers
    button .mainmenu.chrome -width 10 -bg "#ffcc00" -text "Chrome" -command {exec chrome &}
    pack .mainmenu.chrome -side top
    button .mainmenu.firefox -width 10 -bg "#ffcc00" -text "Firefox" -command {exec firefox &}
    pack .mainmenu.firefox -side top

# Others
    button .mainmenu.radiotuner -width 10 -bg "#ffff00" -text "Radiotuner" -command {exec menu_radiotuner.tcl &}
    pack .mainmenu.radiotuner -side top
    button .mainmenu.rdesktop -width 10 -bg "#ffff00" -text "Rdesktop" -command {exec menu_rdesktop.tcl &}
    pack .mainmenu.rdesktop -side top
    button .mainmenu.skype -width 10 -bg "#ffff00" -text "Skype" -command {exec skype &}
    pack .mainmenu.skype -side top
    button .mainmenu.vncviewer -width 10 -bg "#ffff00" -text "VNC Viewer" -command {exec vncviewer &}
    pack .mainmenu.vncviewer -side top
    button .mainmenu.zoom -width 10 -bg "#ffff00" -text "Zoom" -command {exec zoom &}
    pack .mainmenu.zoom -side top


    button .mainmenu.close -width 10 -bg "#ff0000" -text Close -command exit
    pack .mainmenu.close -side top

pack .mainmenu -side top -fill x
