#!/usr/bin/env wish
#
# Add to "/etc/sudoers":
# %users ALL=NOPASSWD:/sbin/poweroff,/sbin/reboot
#

. config -bg "#cccccc"

frame .tools -bg "#cccccc"
    button .tools.kill -width 10 -bg "#ffff00" -text "Kill Window" -command {
        exec xkill &
    }
    pack .tools.kill -side top

    button .tools.settimezone -width 10 -bg "#ffcc00" -text "Set Time Zone" -command {
        exec xsudo sh -c "dpkg-reconfigure tzdata; ntpdate pool.ntp.org" &
    }
    pack .tools.settimezone -side top

    button .tools.keymap -width 10 -bg "#ffcc00" -text "Set Key Map" -command {
        exec keymap.tcl &
    }
    pack .tools.keymap -side top
pack .tools -side top -fill x

frame .session -bg "#cccccc"
    button .session.logout -width 10 -bg "#ffff00" -text "Logout" -command {
        exec xlogout -force &
    }
    pack .session.logout -side top

    button .session.reboot -width 10 -bg "#ffff00" -text "Restart" -command {
        exec sudo /sbin/reboot &
    }
    pack .session.reboot -side top

    button .session.shutdown -width 10 -bg "#ffff00" -text "Shut Down" -command {
        exec sudo /sbin/poweroff &
    }
    pack .session.shutdown -side top
pack .session -side top -fill x

frame .menu -bg "#cccccc"
    button .menu.lock -width 10 -bg "#ff0000" -text "Lock Screen" -command {
        exec lock &
    }
    pack .menu.lock -side top

    button .menu.close -width 10 -bg "#ff0000" -text Close -command exit
    pack .menu.close -side top
pack .menu -side top -fill x
