#!/usr/bin/env bash
#
# Shotcut 26.1.30 (Official) portable app
#

set -e


app_settings() {
    NAME="shotcut"
    VERSION="26.1.30"
    PORT="linux64-x86"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://github.com/mltframework/shotcut/releases/download/v$VERSION/shotcut-linux-x86_64-$VERSION.AppImage
    "
    APP_REMOVE="
        usr/bin/share/shotcut/translations/.lupdate
        usr/share
        usr/lib
    "
    APP_START="AppRun"
    APP_LINK="shotcut"
}

app_start() {
    MYDIR=$(realpath "${0%/*}")
    exec "$MYDIR/$APP_START" "$@"
}


source "${0%/*}/setup-software.bash" app_settings
