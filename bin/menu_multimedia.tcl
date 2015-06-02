#!/usr/bin/env wish

. config -bg "#cccccc"


frame .mainmenu -bg "#cccccc"

# Audio
    button .mainmenu.audacity -width 10 -bg "#ffcc00" -text "Audacity" -command {exec audacity &}
    pack .mainmenu.audacity -side top
    button .mainmenu.audiomixer -width 10 -bg "#ffcc00" -text "Audio Mixer" -command {exec xmixer &}
    pack .mainmenu.audiomixer -side top
    button .mainmenu.zhspeak -width 10 -bg "#ffcc00" -text "ZHSpeak" -command {exec zhspeak -g &}
    pack .mainmenu.zhspeak -side top

# Video
    button .mainmenu.openshot -width 10 -bg "#ffff00" -text "Openshot" -command {exec openshot &}
    pack .mainmenu.openshot -side top
    button .mainmenu.vlc -width 10 -bg "#ffff00" -text "VLC" -command {exec vlc &}
    pack .mainmenu.vlc -side top

    button .mainmenu.close -width 10 -bg "#ff0000" -text Close -command exit
    pack .mainmenu.close -side top

pack .mainmenu -side top -fill x
