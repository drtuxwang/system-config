#!/usr/bin/env wish

. config -bg "#cccccc"


frame .mainmenu -bg "#cccccc"

    button .mainmenu.evince -width 10 -bg "#ffcc00" -text Evince -command {exec evince &}
    pack .mainmenu.evince -side top
    button .mainmenu.libreoffice -width 10 -bg "#ffcc00" -text "LibreOffice" -command {exec soffice &}
    pack .mainmenu.libreoffice -side top
    button .mainmenu.xedit -width 10 -bg "#ffcc00" -text Xedit -command {exec xedit &}
    pack .mainmenu.xedit -side top

    button .mainmenu.close -width 10 -bg "#ff0000" -text Close -command exit
    pack .mainmenu.close -side top

pack .mainmenu -side top -fill x
