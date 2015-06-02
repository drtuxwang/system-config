#!/usr/bin/env wish
#
# Add to "/etc/sudoers":
# %users ALL=NOPASSWD:/sbin/poweroff,/sbin/reboot
#

. config -bg "#cccccc"


frame .mainmenu -bg "#cccccc"

# Tools
    button .mainmenu.settimezone -width 10 -bg "#ffcc00" -text "Set Time Zone" -command {exec xsudo sh -c "dpkg-reconfigure tzdata; ntpdate pool.ntp.org" &}
    pack .mainmenu.settimezone -side top
    button .mainmenu.keymap -width 10 -bg "#ffcc00" -text "Set Key Map" -command {exec keymap.tcl &}
    pack .mainmenu.keymap -side top
    button .mainmenu.xlock -width 10 -bg "#ffcc00" -text "Lock Screen" -command {exec xlock &}
    pack .mainmenu.xlock -side top

# Logout
    button .mainmenu.logout -width 10 -bg "#ffff00" -text "Logout" -command {exec xlogout &}
    pack .mainmenu.logout -side top
    button .mainmenu.reboot -width 10 -bg "#ffff00" -text "Restart" -command {exec sudo /sbin/reboot &}
    pack .mainmenu.reboot -side top
    button .mainmenu.shutdown -width 10 -bg "#ffff00" -text "Shut Down" -command {exec sudo /sbin/poweroff &}
    pack .mainmenu.shutdown -side top

    button .mainmenu.close -width 10 -bg "#ff0000" -text Close -command exit
    pack .mainmenu.close -side top

pack .mainmenu -side top -fill x

