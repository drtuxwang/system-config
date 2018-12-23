# Fix display resolution:
# set_vga VGA-0 1024 768 60 &
# set_vga VGA1 1440 900 60 &
# xreset DVI-I=1360x768

# Fix audio settings:
# pactl set-card-profile 0 output:hdmi-stereo+input:analog-stereo  # HDMI-1
# pactl set-card-profile 0 output:hdmi-stereo-extra1+input:analog-stereo  # HDMI-2
# pactl set-card-profile 0 off
# pactl set-sink-volume 0 100%  # pactl list short sinks

# Fix mouse speed:
# xset m 2,16

# Fix keyboard language:
# setxkbmap us  # "gb", "de", "us"

# Start applications:
# start_app -pname=chromium-browser -timeout=60 chromium &
# start_app -pname=google-chrome -timeout=60 chrome &
# start_app -timeout=60 firefox &
# myqsd 1
