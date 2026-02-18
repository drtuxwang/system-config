#!/usr/bin/env bash
#
# Asmc 2.37.67 (Official) portable app
#

set -e


app_settings() {
    NAME="asmc"
    VERSION="2.37.67"
    PORT="linux64-x86"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://github.com/nidud/asmc/raw/28f72c9f68cea24632a7338839141b2eefdb4aa7/bin/asmc64
    "
    APP_SHELL="
        chmod 755 asmc64
    "
    APP_START="asmc64"
    APP_LINK="asmc"
}

app_start() {
    MYDIR=$(realpath "${0%/*}")
    exec "$MYDIR/$APP_START" "$@"
}


source "${0%/*}/setup-software.bash" app_settings
