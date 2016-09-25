#!/bin/sh

set_vga()
{   
    MODELINE=$(gtf 1440 900 60 | grep Modeline | awk '{
        printf("%4.2f %d %d %d %d %d %d %d %d\n", $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
    }')
    echo xrandr --newmode $2x${3}_$4 $MODELINE
    echo xrandr --addmode $1 $2x${3}_$4
    echo xrandr -s $2x$3
}

start_app()
{
    echo "Starting \"$1\"..."
    "$@" &
    sleep 4
    for _ in `seq 11`; do
        sleep 1
        if [ ! "`ps | grep \" $1\$\"`" ]; then
            echo "Restarting \"$1\"..."
            "$@" &
            break
        fi
    done
}


if [ "`lspci 2> /dev/null | grep VirtualBox`" ]; then
    (sleep 1; xrandr --dpi 96; sleep 1; xrandr -s 1024x768) &
fi
# set_vga VGA1 gtf 1440 900 60
# xreset
# setxkbmap us  # "gb", "de", "us"
# xset m 2,16  # Slow mouse

# start_app chrome &
# start_app firefox &
# myqsd 1
