#!/usr/bin/env wish

. config -bg "#cccccc"

frame .browser -bg "#cccccc"
    button .browser.chrome -width 10 -bg "#ffcc00" -text "Chrome" -command {
        exec chrome &
    }
    pack .browser.chrome -side top

    button .browser.chromium -width 10 -bg "#ffcc00" -text "Chromium" -command {
        exec chromium &
    }
    pack .browser.chrome -side top

    button .browser.firefox -width 10 -bg "#ffcc00" -text "Firefox" -command {
        exec firefox &
    }
    pack .browser.firefox -side top
pack .browser -side top -fill x

frame .other -bg "#cccccc"
    button .other.radiotuner -width 10 -bg "#ffff00" -text "Radiotuner" -command {
        exec menu_radiotuner.tcl &
    }
    pack .other.radiotuner -side top

    button .other.vncviewer -width 10 -bg "#ffff00" -text "VNC Viewer" -command {
        exec vncviewer &
    }
    pack .other.vncviewer -side top

    button .other.xfreerdp -width 10 -bg "#ffff00" -text "X FreeRDP" -command {
        exec xfreerdp.tcl &
    }
    pack .other.xfreerdp -side top
pack .other -side top -fill x

frame .menu -bg "#cccccc"
    button .menu.close -width 10 -bg "#ff0000" -text Close -command exit
    pack .menu.close -side top
pack .menu -side top -fill x
