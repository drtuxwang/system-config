#!/usr/bin/env wish

. config -bg "#cccccc"

frame .tools -bg "#cccccc"
    button .tools.breaktimer -width 10 -bg "#ffcc00" -text "Break Timer" -command {
        exec breaktimer -g 10 &
    }
    pack .tools.breaktimer -side top

    button .tools.calculator -width 10 -bg "#ffcc00" -text "Calculator" -command {
        exec xcalc &
    }
    pack .tools.calculator -side top

     button .tools.calendar -width 10 -bg "#ffcc00" -text "Calendar" -command {
        exec orage &
    }
    pack .tools.calendar -side top

    button .tools.ibus -width 10 -bg "#ffcc00" -text "Ibus Input" -command {
        exec ibus-daemon &
    }
    pack .tools.ibus -side top

    button .tools.keyboard -width 10 -bg "#ffcc00" -text "Keyboard" -command {
        exec xvkbd &
    }
    pack .tools.keyboard -side top
pack .tools -side top -fill x

frame .system -bg "#cccccc"
    button .system.printer -width 10 -bg "#ffff00" -text "Printer" -command {
        exec system-config-printer &
    }
    pack .system.printer -side top

    button .system.kill -width 10 -bg "#ffff00" -text "Xkill" -command {
        exec xkill &
    }
    pack .system.kill -side top

    button .system.xrun -width 10 -bg "#ffff00" -text "Xrun" -command {
        exec xrun.tcl &
    }
    pack .system.xrun -side top
pack .system -side top -fill x

frame .menu -bg "#cccccc"
    button .menu.close -width 10 -bg "#ff0000" -text Close -command exit
    pack .menu.close -side top
pack .menu -side top -fill x

