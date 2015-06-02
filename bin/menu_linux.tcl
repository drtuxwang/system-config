#!/usr/bin/env wish

. config -bg "#cccccc"


frame .mainmenu -bg "#cccccc"

# Desktop
    button .mainmenu.hotdog -width 10 -bg "#ffcc00" -text "hotdog" -command {exec xterm hotdog.local &}
    pack .mainmenu.hotdog -side top
    button .mainmenu.xiaobear -width 10 -bg "#ffcc00" -text "xiaobear" -command {exec xterm xiaobear.local &}
    pack .mainmenu.xiaobear -side top
    button .mainmenu.webtv -width 10 -bg "#ffcc00" -text "webtv" -command {exec xterm webtv.local &}
    pack .mainmenu.webtv -side top

# Portable
    button .mainmenu.netbook -width 10 -bg "#ffff00" -text "netbook" -command {exec xterm netbook.local &}
    pack .mainmenu.netbook -side top

    button .mainmenu.close -width 10 -bg "#ff0000" -text Close -command exit
    pack .mainmenu.close -side top

pack .mainmenu -side top -fill x
