#!/usr/bin/env wish

. config -bg "#cccccc"

frame .tool -bg "#cccccc"
    button .tool.gimp -width 10 -bg "#ffcc00" -text "Gimp" -command {
        exec gimp &
    }
    pack .tool.gimp -side top

    button .tool.geeqie -width 10 -bg "#ffcc00" -text "Geeqie" -command {
        exec gqview &
    }
    pack .tool.geeqie -side top

    button .tool.xsane -width 10 -bg "#ffcc00" -text "Xsane" -command {
        exec xsane &
    }
    pack .tool.xsane -side top

    button .tool.screenshot -width 10 -bg "#ffff00" -text ScreenShot -command {
        exec xsnapshot &
    }
    pack .tool.screenshot -side top
pack .tool -fill x

frame .menu -bg "#cccccc"
    button .menu.close -width 10 -bg "#ff0000" -text Close -command exit
    pack .menu.close -side top
pack .menu -side top -fill x
