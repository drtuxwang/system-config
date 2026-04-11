#!/usr/bin/env bash
#
# Inkscape 1.3.2 (Official) portable app
#

set -e


app_settings() {
    NAME="inkscape"
    VERSION="1.3.2"
    PORT="linux64-x86"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://inkscape.org/gallery/item/44616/Inkscape-091e20e-x86_64.AppImage
    "
    APP_REMOVE="
        org.inkscape.Inkscape.desktop
        org.inkscape.Inkscape.png
        usr/share/man/??
    "
    APP_START="AppRun"
    APP_LINK="inkscape"
}

app_start() {
    MYDIR=$(realpath "${0%/*}")
    exec "$MYDIR/$APP_START" "$@"
}


source "${0%/*}/setup-software.bash" app_settings
