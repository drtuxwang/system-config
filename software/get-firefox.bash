#!/usr/bin/env bash
#
# Firefox 140.6.0esr (Official) portable app
#

set -e


app_settings() {
    NAME="firefox"
    VERSION="140.6.0esr"
    PORT="linux64-x86"

    APP_DIRECTORY="${NAME}_stable-$PORT"
    APP_FILES="
        https://ftp.mozilla.org/pub/firefox/releases/$VERSION/linux-x86_64/en-GB/firefox-$VERSION.tar.xz
    "
    APP_REMOVE="
        firefox/icons/
    "
    APP_SHELL="
        mv firefox/ firefox-stable/
        mv firefox-stable/* .
        rm -r firefox-stable/
    "
    APP_START="firefox"
}

app_start() {
    MYDIR=$(realpath "${0%/*}")
    exec "$MYDIR/$APP_START" "$@"
}


source "${0%/*}/setup-software.bash" app_settings
