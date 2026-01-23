set_vga() {
    MODELINE=$(gtf $2 $3 $4 | grep Modeline | awk '{
        printf("%4.2f %d %d %d %d %d %d %d %d\n", $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
    }')
    xrandr --newmode $2x${3}_$4 $MODELINE
    xrandr --addmode $1 $2x${3}_$4
    xrandr --dpi 96
    sleep 1
    xrandr -s $2x${3}_$4
}


# Fix display
##set_vga VGA-0 1024 768 60 &
##set_vga VGA1 1440 900 60 &
##xreset DVI-I=1360x768 &
##xreset Virtual1=1440x900 &
##xrandr --dpi 96

# Fix pulseaudio volume (pactl list short sinks)
##pactl set-sink-volume 0 100%
# Fix pipewire aduio volume (wpctl status):
##wpctl set-volume @DEFAULT_AUDIO_SINK@ 1.0

# Fix keyboard (xmodmap -pke, xev)
##setxkbmap us
##xmodmap -e "keycode 94 = grave notsign grave notsign bar bar bar"
##xmodmap -e "keycode 49 = backslash bar backslash bar bar brokenbar bar"
# Fix mouse:
##xset m 4,16

# Start browser: 1920x1080(FHD), 1920x1200(WUXGA), 2560x1440(QHD), 3840x2160(4K UHD)
##XWEB_SIZE=1920x1080 XWEB_TABS=3 xweb &

# MyQS daemon slots
##myqsd 4
