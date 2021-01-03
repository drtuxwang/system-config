#!/usr/bin/env wish

wm resizable . 0 0
wm title . "Zhong Hua Speak v5.1.0"
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

    button .toolbar.en -width 4 -bg "#00ff00" -text en -command {
        catch {exec zhspeak -en "$text"} msg
    }
    pack .toolbar.en -side left
    button .toolbar.de -width 4 -bg "#ffff00" -text de -command {
        catch {exec zhspeak -de "$text"} msg
    }
    pack .toolbar.de -side left
    button .toolbar.es -width 4 -bg "#ffff00" -text es -command {
        catch {exec zhspeak -es "$text"} msg
    }
    pack .toolbar.es -side left
    button .toolbar.fr -width 4 -bg "#ffff00" -text fr -command {
        catch {exec zhspeak -fr "$text"} msg
    }
    pack .toolbar.fr -side left
    button .toolbar.it -width 4 -bg "#ffff00" -text it -command {
       catch {exec zhspeak -it "$text"} msg
    }
    pack .toolbar.it -side left

    button .toolbar.zh -width 4 -bg "#00ff00" -text 普通話 -command {
        catch {exec zhspeak -zh "$text"} msg
    }
    pack .toolbar.zh -side left
    button .toolbar.pinyin -width 4 -bg "#00ff00" -text 拼音 -command {
        catch {exec zhspeak -pinyin -zh "$text"} msg
    }
    pack .toolbar.pinyin -side left
    button .toolbar.zhy -width 4 -bg "#00ff00" -text 粵語 -command {
        catch {exec zhspeak -zhy "$text"} msg
    }
    pack .toolbar.zhy -side left
    button .toolbar.jyutping -width 4 -bg "#00ff00" -text 粵拼 -command {
        catch {exec zhspeak -pinyin -zhy "$text"} msg
    }
    pack .toolbar.jyutping -side left

    button .toolbar.close -width 4 -bg "#ff0000" -text Close -command exit
    pack .toolbar.close -side right
pack .toolbar -side top -fill x


frame .output -bg "#cccccc"

    entry .output.msg -width 100 -bg "#cccccc" -text msg
    pack .output.msg -side left

pack .output -side top -fill x


set text {Please type or copy text here}
set output {Output text...}
