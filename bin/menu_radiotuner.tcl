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
    button .mainmenu.rthk -width 10 -bg "#ffff00" -text "RTHK" -command {exec firefox http://programme.rthk.hk/channel/radio/player_popup.php?rid=168&player=mp3&type=live &}
    pack .mainmenu.rthk -side top

    button .mainmenu.close -width 10 -bg "#ff0000" -text Close -command exit
    pack .mainmenu.close -side top

pack .mainmenu -side top -fill x
