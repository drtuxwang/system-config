#!/usr/bin/env wish

. config -bg "#cccccc"


frame .location -bg "#cccccc"
    entry .location.hostname -width 26 -relief sunken -textvar hostname
    pack .location.hostname -side top
pack .location -fill x

frame .login -bg "#cccccc"
    entry .login.username -width 13 -relief sunken -textvar username
    pack .login.username -side left
    entry .login.password -width 13 -relief sunken -textvar password -show "*"
    pack .login.password -side left
pack .login -fill x

frame .connect -bg "#cccccc"
    entry .connect.size -width 13 -relief sunken -textvar size
    pack .connect.size -side left
    button .connect.run -width 10 -bg "#00ff00" -text "Connect" -command {
        exec xfreerdp /cert-ignore /v:${hostname} /size:${size} /u:${username} /p:${password} &
    }
    pack .connect.run -side left
pack .connect -fill x

set hostname {hostname.local}
set username {domain\user}
set password {???}
set size {1024x768}
