#!/usr/bin/env bash
#
# curl-impersonate 2.3.1 (Official) portable app
#

set -e


app_settings() {
    NAME="curl-impersonate"
    VERSION="2.3.1"
    FIREFOX="153"
    PORT="linux64-x86"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://github.com/lexiforest/curl-impersonate/releases/download/v$VERSION/curl-impersonate-v$VERSION.x86_64-linux-gnu.tar.gz
    "
    APP_SHELL="
        strip curl-impersonate
        touch -r LICENSE curl-impersonate
        mkdir bin
        mv LICENSE** curl* bin/
    "
    APP_START="bin/curl-impersonate"
    APP_LINK="curl-chrome curl-firefox"
}

app_start() {
    MYDIR=$(realpath "${0%/*}")
    [ "${0##*/}" = curl-chrome ] && APP_START="bin/$(ls -1vr "$MYDIR/bin" | awk '/curl_chrome.*[0-9]$/ {print; exit}')"
    [ "${0##*/}" = curl-firefox ] && APP_START="bin/curl_firefox153"
    [ "${_SANDBOX_PARENT:-}" ] && exec "$MYDIR/$APP_START" "$@"
    [ "$1" = "--version" ] && "$0" -v --version 2>&1 | sed -e "s@impersonate/local@impersonate/$VERSION@" 1>&2 && exit
    exec /usr/bin/bwrap \
        --ro-bind / / \
        --tmpfs /home \
        --tmpfs /media \
        --tmpfs /mnt \
        --tmpfs /tmp \
        -- "$MYDIR/$APP_START" "$@"
}


source "${0%/*}/setup-software.bash" "$@" app_settings
