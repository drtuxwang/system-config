#!/usr/bin/env wish

. config -bg "#cccccc"


frame .input -bg "#cccccc"

    entry .input.command -width 100 -relief sunken -textvar command
    pack .input.command -side left

pack .input -side top -fill x


frame .toolbar -bg "#cccccc"

    pack .toolbar -side top -fill x

    button .toolbar.cut -width 4 -bg "#ff0000" -text "Cut" -command {set command {}}
    pack .toolbar.cut -side left
    button .toolbar.copy -width 4 -bg "#ffcc00" -text "Copy" -command {
        exec echo "$command" | xclip -in &
    }
    pack .toolbar.copy -side left
    button .toolbar.paste -width 4 -bg "#ffcc00" -text "Paste" -command {
        catch {exec xclip -out -selection -c text} command
    }
    pack .toolbar.paste -side left
    button .toolbar.run -width 4 -bg "#00ff00" -text "Run" -command {
        cd $directory; exec xrun -split $command &
    }
    pack .toolbar.run -side left

    entry .toolbar.directory -width 70 -relief sunken -textvar directory
    pack .toolbar.directory -side right
pack .toolbar -side top -fill x

set command {Please type or copy text here}
set directory $::env(HOME)
if [file exists $::env(HOME)/Desktop/Downloads] {
    set directory $::env(HOME)/Desktop/Downloads
}
