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


# Fix display:
##set_vga VGA-0 1024 768 60 &
##set_vga VGA1 1440 900 60 &
##xreset DVI-I=1360x768 &
##xreset Virtual1=1280x720 &
##xrandr --dpi 96

# Fix audio (pactl list short sinks):
##pactl set-card-profile 0 output:hdmi-stereo+input:analog-stereo  # HDMI-1
##pactl set-card-profile 0 output:hdmi-stereo-extra1+input:analog-stereo  # HDMI-2
##pactl set-card-profile 0 off
##pactl set-sink-volume 0 50%  # Default volume from 0% to 153%

# Fix keyboard (xmodmap -pke, xev)
##setxkbmap us
##xmodmap -e "keycode 94 = grave notsign grave notsign bar bar bar"
##xmodmap -e "keycode 49 = backslash bar backslash bar bar brokenbar bar"

# Fix mouse:
##xset m 4,16

# Start applications:
##XWEB_TABS=3 xweb &
##myqsd 1
