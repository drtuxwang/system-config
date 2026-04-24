#!/usr/bin/env bash
#
# WiNE 11.0 (Offical) bubblewrap portable app
# - Requires: bwrap (Bubblewrap)
#

set -e


app_settings() {
    NAME="wine"
    VERSION="11.0"
    PORT="linux64-x86-glibc_2.41"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    REPO="https://dl.winehq.org/wine-builds/debian/pool"
    APP_FILES="
        $REPO/main/w/wine/wine-stable_11.0.0.0~trixie-1_amd64.deb
        $REPO/main/w/wine/wine-stable-amd64_11.0.0.0~trixie-1_amd64.deb
        $REPO/main/w/wine/wine-stable-i386_11.0.0.0~trixie-1_i386.deb
    "
    APP_REMOVE="
        opt/wine-stable/share/man/*.UTF-8
        usr/share/doc
        usr/
    "
    APP_START="opt/wine-stable/bin/wine"
    APP_LINK="wine"
}

app_start() {
    MYDIR=$(realpath "${0%/*}")
    [ "${_SANDBOX_PARENT:-}" ] && exec "$MYDIR/$APP_START" "$@"
    [ ! -d "$HOME/.wine" ] && mkdir "$HOME/.wine"
    exec /usr/bin/bwrap \
        --ro-bind / / \
        --tmpfs /home \
        --tmpfs /tmp \
        --dev dev \
        --dev-bind-try /dev/dri /dev/dri \
        --bind-try /run/user/$(id -u)/pulse /run/user/$(id -u)/pulse \
        --bind-try "$HOME/.wine" "$HOME/.wine" \
        -- "$MYDIR/$APP_START" "$@"
}


source "${0%/*}/setup-software.bash" app_settings
