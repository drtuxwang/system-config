#!/usr/bin/env wish

. config -bg "#cccccc"


frame .mainmenu -bg "#cccccc"

# English
    button .mainmenu.bbcradio -width 10 -bg "#ffcc00" -text "BBC Radios" -command {exec firefox http://www.bbc.co.uk/radio/player/bbc_radio_one &}
    pack .mainmenu.bbcradio -side top
    button .mainmenu.magic -width 10 -bg "#ffcc00" -text "Magic 105.4" -command {exec vlc --http-reconnect http://tx.whatson.com/icecast.php?i=magic1054.mp3 &}
    pack .mainmenu.magic -side top

# Chinese
    button .mainmenu.988 -width 10 -bg "#ffff00" -text "988最好听" -command {exec vlc --http-reconnect http://starrfm.rastream.com/starrfm-988 &}
    pack .mainmenu.988 -side top
    button .mainmenu.rthk1 -width 10 -bg "#ffff00" -text "RTHK 1" -command {exec vlc --http-reconnect http://rthk.hk/live1.m3u &}
    pack .mainmenu.rthk1 -side top
    button .mainmenu.rthk2 -width 10 -bg "#ffff00" -text "RTHK 2" -command {exec vlc --http-reconnect http://rthk.hk/live2.m3u &}
    pack .mainmenu.rthk2 -side top
    button .mainmenu.rthk3 -width 10 -bg "#ffff00" -text "RTHK 3" -command {exec vlc --http-reconnect http://rthk.hk/live3.m3u &}
    pack .mainmenu.rthk3 -side top
    button .mainmenu.rthk4 -width 10 -bg "#ffff00" -text "RTHK 4" -command {exec vlc --http-reconnect http://rthk.hk/live4.m3u &}
    pack .mainmenu.rthk4 -side top
    button .mainmenu.rthk5 -width 10 -bg "#ffff00" -text "RTHK 5" -command {exec vlc --http-reconnect http://rthk.hk/live5.m3u &}
    pack .mainmenu.rthk5 -side top
    button .mainmenu.rthkpth -width 10 -bg "#ffff00" -text "RTHK普通話" -command {exec vlc --http-reconnect http://rthk.hk/livepth.m3u &}
    pack .mainmenu.rthkpth -side top

    button .mainmenu.close -width 10 -bg "#ff0000" -text Close -command exit
    pack .mainmenu.close -side top

pack .mainmenu -side top -fill x
