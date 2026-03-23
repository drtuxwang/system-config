#!/usr/bin/env bash
#
# Audacity 3.6.4 (Official) portable app
#

set -e


app_settings() {
    NAME="audacity"
    VERSION="3.6.4"
    PORT="linux64-x86"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://github.com/audacity/audacity/releases/download/Audacity-$VERSION/audacity-linux-$VERSION-x64.AppImage
    "
    APP_REMOVE="
        audacity
        audacity.desktop
        audacity.svg
        share/audacity/plug-ins/rms.ny
        share/icons/hicolor/16x16/apps
        share/icons/hicolor/32x32/apps
        share/icons/hicolor/64x64
        share/icons/hicolor/128x128
        share/icons/hicolor/256x256
    "
    APP_START="AppRun"
    APP_LINK="audacity"
}

app_start() {
    MYDIR=$(realpath "${0%/*}")
    if [ "${1:-}" = "--version" ]
    then
        grep version= "$MYDIR/bin/check_dependencies" | cut -f2 -d'"'
    else
        exec "$MYDIR/$APP_START" "$@"
    fi
}


source "${0%/*}/setup-software.bash" app_settings
