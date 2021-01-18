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

start_app() {
    NAME=
    TIMEOUT=10
    while [[ $1 = -* ]]
    do
        case $1 in
        -pname=*)
            NAME=`echo "$1" | cut -f2- -d"="`
            ;;
        -timeout=*)
            TIMEOUT=`echo "$1" | cut -f2- -d"="`
            ;;
        esac
        shift
    done
    if [ ! "$NAME" ]
    then
        NAME=$1
    fi

    echo "Starting \"$@\"..."
    "$@" &
    sleep 10
    for DELAY in $(seq 11 $TIMEOUT)
    do
        if [ ! "$(ps -o "args" | sed -e "s/^/ /" -e "s/\$/ /" | grep "[ /]$NAME ")" ]
        then
            echo "Restarting \"$1\" after $DELAY seconds..."
            "$@" &
            return
        fi
        sleep 1
    done
    echo "Running \"$@\"..."
}


# Fix display resolution:
##set_vga VGA-0 1024 768 60 &
##set_vga VGA1 1440 900 60 &
##xreset DVI-I=1360x768

# Fix audio settings (pactl list short sinks):
##pactl set-card-profile 0 output:hdmi-stereo+input:analog-stereo  # HDMI-1
##pactl set-card-profile 0 output:hdmi-stereo-extra1+input:analog-stereo  # HDMI-2
##pactl set-card-profile 0 off
##pactl set-sink-volume 0 300%  # Workaround speaker hiss

# Fix mouse speed:
##xset m 2,16

# Fix keyboard language:
##setxkbmap us  # "gb", "de", "us"

# Start applications:
##start_app -pname=chromium-browser -timeout=60 chromium &
##start_app -pname=google-chrome -timeout=60 chrome &
##start_app -timeout=60 firefox &
##myqsd 1
