#!/usr/bin/env wish

. config -bg "#cccccc"

frame .english -bg "#cccccc"
    button .english.bbcradio -width 10 -bg "#ffcc00" -text "BBC Radios" -command {
        exec firefox http://www.bbc.co.uk/radio/player/bbc_radio_one &
    }
    pack .english.bbcradio -side top

    button .english.magic -width 10 -bg "#ffcc00" -text "Magic 105.4" -command {
        exec vlc --http-reconnect http://tx.whatson.com/icecast.php?i=magic1054.mp3 &
    }
    pack .english.magic -side top
pack .english -side top -fill x

frame .chinese -bg "#cccccc"
    button .chinese.988 -width 10 -bg "#ffff00" -text "988最好听" -command {
        exec vlc --http-reconnect http://starrfm.rastream.com/starrfm-988 &
    }
    pack .chinese.988 -side top

    button .chinese.rthk -width 10 -bg "#ffff00" -text "RTHK Radios" -command {
        exec firefox http://programme.rthk.hk/channel/radio/player_popup.php?rid=168&player=mp3&type=live &
    }
    pack .chinese.rthk -side top

    button .chinese.rthk1 -width 10 -bg "#ffff00" -text "RTHK 1" -command {
        exec vlc --http-reconnect http://rthk.hk/live1.m3u &
    }
    pack .chinese.rthk1 -side top

    button .chinese.rthk2 -width 10 -bg "#ffff00" -text "RTHK 2" -command {
        exec vlc --http-reconnect http://rthk.hk/live2.m3u &
    }
    pack .chinese.rthk2 -side top

    button .chinese.rthk3 -width 10 -bg "#ffff00" -text "RTHK 3" -command {
        exec vlc --http-reconnect http://rthk.hk/live3.m3u &
    }
    pack .chinese.rthk3 -side top

    button .chinese.rthk4 -width 10 -bg "#ffff00" -text "RTHK 4" -command {
        exec vlc --http-reconnect http://rthk.hk/live4.m3u &
    }
    pack .chinese.rthk4 -side top

    button .chinese.rthk5 -width 10 -bg "#ffff00" -text "RTHK 5" -command {
        exec vlc --http-reconnect http://rthk.hk/live5.m3u &
    }
    pack .chinese.rthk5 -side top

    button .chinese.rthkpth -width 10 -bg "#ffff00" -text "RTHK普通話" -command {
        exec vlc --http-reconnect http://rthk.hk/livepth.m3u &
    }
    pack .chinese.rthkpth -side top
pack .chinese -side top -fill x

frame .menu -bg "#cccccc"
    button .menu.close -width 10 -bg "#ff0000" -text Close -command exit
    pack .menu.close -side top
pack .menu -side top -fill x
