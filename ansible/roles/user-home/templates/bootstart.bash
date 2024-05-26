#!/usr/bin/env bash

# Optional input environment
ARG=${1:-}

# Fix logging
[ "$ARG" != "-start" ] && mkdir -p /tmp/$(id -un) && exec $0 -start > /tmp/$(id -un)/.bootstart.log 2>&1

# Setup bash
export TERM=xterm
source $HOME/.profile
[ ! "$BASE_PATH" ] && export BASE_PATH="$PATH"
export PATH="$HOME/software/scripts:$HOME/software/bin:/opt/software/bin:$BASE_PATH"
export TMPDIR=${TMPDIR:-/tmp/$(id -un)}

# Update "/home/owner/software/web-data/pages" web pages
sleep 300 && $HOME/software/scripts/pull-web.bash &

# Start VNC Server for VMs and live boot
{% if vncserver %}
echo x | vncserver -SecurityTypes=None &
{% else %}
##echo x | vncserver -SecurityTypes=None &
{% endif %}
