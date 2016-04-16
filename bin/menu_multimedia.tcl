#!/usr/bin/env wish

. config -bg "#cccccc"

frame .audio -bg "#cccccc"
    button .audio.audacity -width 10 -bg "#ffcc00" -text "Audacity" -command {
        exec audacity &
    }
    pack .audio.audacity -side top

    button .audio.audiomixer -width 10 -bg "#ffcc00" -text "Audio Mixer" -command {
        exec xmixer &
    }
    pack .audio.audiomixer -side top

    button .audio.zhspeak -width 10 -bg "#ffcc00" -text "ZHSpeak" -command {
        exec zhspeak -g &
    }
    pack .audio.zhspeak -side top
pack .audio -side top -fill x

frame .video -bg "#cccccc"
    button .video.openshot -width 10 -bg "#ffff00" -text "Openshot" -command {
        exec openshot &
    }
    pack .video.openshot -side top

    button .video.vlc -width 10 -bg "#ffff00" -text "VLC" -command {
       exec vlc &
    }
    pack .video.vlc -side top
pack .video -side top -fill x

frame .menu -bg "#cccccc"
    button .menu.close -width 10 -bg "#ff0000" -text Close -command exit
    pack .menu.close -side top
pack .menu -side top -fill x
