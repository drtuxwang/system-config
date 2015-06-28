#!/usr/bin/env wish

. config -bg "#cccccc"


frame .mainmenu -bg "#cccccc"

# Tools
   button .mainmenu.alarmclock -width 10 -bg "#ffcc00" -text "Alarm Clock" -command {exec alarmclock &}
   pack .mainmenu.alarmclock -side top
   button .mainmenu.breaktimer -width 10 -bg "#ffcc00" -text "Break Timer" -command {exec breaktimer -g 10 &}
   pack .mainmenu.breaktimer -side top
   button .mainmenu.calculator -width 10 -bg "#ffcc00" -text "Calculator" -command {exec xcalc &}
   pack .mainmenu.calculator -side top
   button .mainmenu.calendar -width 10 -bg "#ffcc00" -text "Calendar" -command {exec orage &}
   pack .mainmenu.calendar -side top
   button .mainmenu.ibus -width 10 -bg "#ffcc00" -text "Ibus Input" -command {exec ibus-daemon &}
   pack .mainmenu.ibus -side top
   button .mainmenu.keyboard -width 10 -bg "#ffcc00" -text "Keyboard" -command {exec xvkbd &}
   pack .mainmenu.keyboard -side top

# System tools
   button .mainmenu.printer -width 10 -bg "#ffff00" -text "Printer" -command {exec system-config-printer &}
   pack .mainmenu.printer -side top
   button .mainmenu.vbox -width 10 -bg "#ffff00" -text "VirtualBox" -command {exec VirtualBox &}
   pack .mainmenu.vbox -side top

   button .mainmenu.close -width 10 -bg "#ff0000" -text Close -command exit
   pack .mainmenu.close -side top

pack .mainmenu -side top -fill x
