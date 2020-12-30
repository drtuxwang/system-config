#!/usr/bin/env wish

wm resizable . 0 0
wm title . "zhspeak"
wm geometry . +120+20

. config -bg "#cccccc"


frame .input -bg "#cccccc"

    entry .input.text -width 100 -relief sunken -textvar text
    pack .input.text -side left

pack .input -side top -fill x


frame .toolbar -bg "#cccccc"

    pack .toolbar -side top -fill x
    button .toolbar.new -width 4 -bg "#ffcc00" -text "New" -command {set text {}; set msg {}}
    pack .toolbar.new -side left

    button .toolbar.copy -width 4 -bg "#ffcc00" -text "Copy" -command {
        exec echo "$command" | xclip -in &
    }
    pack .toolbar.copy -side left
    button .toolbar.paste -width 4 -bg "#ffcc00" -text "Paste" -command {
        catch {exec xclip -out -selection -c text} text; set msg {}
    }
    pack .toolbar.paste -side left

    button .toolbar.close -width 4 -bg "#ff0000" -text Close -command exit
    pack .toolbar.close -side right
    button .toolbar.pinyin -width 3 -bg "#00ff00" -text py -command {
        catch {exec zhspeak -pinyin -zh "$text"} msg
    }
    pack .toolbar.pinyin -side right
    button .toolbar.zhy -width 3 -bg "#00ff00" -text zhy -command {
        catch {exec zhspeak -zhy "$text"} msg
    }
    pack .toolbar.zhy -side right
    button .toolbar.zh -width 3 -bg "#00ff00" -text zh -command {
        catch {exec zhspeak -zh "$text"} msg
    }
    pack .toolbar.zh -side right
    button .toolbar.en -width 3 -bg "#00ff00" -text en -command {
        catch {exec zhspeak -en "$text"} msg
    }
    pack .toolbar.en -side right

    button .toolbar.sr -width 3 -bg "#ffff00" -text sr -command {
       catch {exec zhspeak -sr "$text"} msg
    }
    pack .toolbar.sr -side right
    button .toolbar.ru -width 3 -bg "#ffff00" -text ru -command {
        catch {exec zhspeak -ru "$text"} msg
    }
    pack .toolbar.ru -side right
    button .toolbar.it -width 3 -bg "#ffff00" -text it -command {
       catch {exec zhspeak -it "$text"} msg
    }
    pack .toolbar.it -side right
    button .toolbar.fr -width 3 -bg "#ffff00" -text fr -command {
        catch {exec zhspeak -fr "$text"} msg
    }
    pack .toolbar.fr -side right
    button .toolbar.es -width 3 -bg "#ffff00" -text es -command {
        catch {exec zhspeak -es "$text"} msg
    }
    pack .toolbar.es -side right
    button .toolbar.de -width 3 -bg "#ffff00" -text de -command {
        catch {exec zhspeak -de "$text"} msg
    }
    pack .toolbar.de -side right

pack .toolbar -side top -fill x


frame .output -bg "#cccccc"

    entry .output.msg -width 100 -bg "#cccccc" -text msg
    pack .output.msg -side left

pack .output -side top -fill x


set text {Please type or copy text here}
set output {Output text...}
