#!/usr/bin/env wish

. config -bg "#cccccc"


frame .mainmenu -bg "#cccccc"

    button .mainmenu.gimp -width 10 -bg "#ffcc00" -text "Gimp" -command {exec gimp &}
    pack .mainmenu.gimp -side top
    button .mainmenu.geeqie -width 10 -bg "#ffcc00" -text "Geeqie" -command {exec gqview &}
    pack .mainmenu.geeqie -side top
    button .mainmenu.inkscape -width 10 -bg "#ffcc00" -text "Inkscape" -command {exec inkscape &}
    pack .mainmenu.inkscape -side top
    button .mainmenu.xsane -width 10 -bg "#ffcc00" -text "Xsane" -command {exec xsane &}
    pack .mainmenu.xsane -side top
    button .mainmenu.screenshot -width 10 -bg "#ffff00" -text ScreenShot -command {exec xsnapshot &}
    pack .mainmenu.screenshot -side top

    button .mainmenu.close -width 10 -bg "#ff0000" -text Close -command exit
    pack .mainmenu.close -side top

pack .mainmenu -side top -fill x
