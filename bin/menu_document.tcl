#!/usr/bin/env wish

. config -bg "#cccccc"

frame .tool -bg "#cccccc"
    button .tool.evince -width 10 -bg "#ffcc00" -text Evince -command {
        exec evince &
    }
    pack .tool.evince -side top

    button .tool.libreoffice -width 10 -bg "#ffcc00" -text "LibreOffice" -command {
        exec soffice &
    }
    pack .tool.libreoffice -side top

    button .tool.xedit -width 10 -bg "#ffcc00" -text Xedit -command {
        exec xedit &
    }
    pack .tool.xedit -side top
pack .tool -fill x

frame .menu -bg "#cccccc"
    button .menu.close -width 10 -bg "#ff0000" -text Close -command exit
    pack .menu.close -side top
pack .menu -side top -fill x
