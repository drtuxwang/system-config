# set_vga VGA-0 1024 768 60 &
# set_vga VGA1 1440 900 60 &
# xreset DVI-I=1360x768
# setxkbmap us  # "gb", "de", "us"
# xset m 2,16  # Slow mouse

# pactl set-card-profile $(pactl list short cards | grep "alsa_card.pci" | awk '{print $1}') output:hdmi-stereo+input:analog-stereo  # HDMI-1
# pactl set-card-profile $(pactl list short cards | grep "alsa_card.pci" | awk '{print $1}') output:hdmi-stereo-extra1+input:analog-stereo  # HDMI-2
# pactl set-card-profile $(pactl list short cards | grep "alsa_card.pci" | awk '{print $1}') off

# start_app -pname=chromium-browser -timeout=60 chromium &
# start_app -pname=google-chrome -timeout=60 chrome &
# start_app firefox &
# myqsd 1
