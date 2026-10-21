#!/usr/bin/env bash
#
# curl-impersonate 2.3.0 (Official) portable app
#

set -e


app_settings() {
    NAME="curl-impersonate"
    VERSION="2.3.0"
    FIREFOX_ESR="curl_firefox153"
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
    case ${0##*/} in
    curl-chrome)
        APP_START="bin/$(ls -1vr "$MYDIR/bin" | awk '/curl_chrome.*[0-9]$/ {print; exit}')"
        ;;
    curl-firefox)
        APP_START="bin/$FIREFOX_ESR"
        ;;
    esac
    [ "${_SANDBOX_PARENT:-}" ] && exec "$MYDIR/$APP_START" "$@"
    exec /usr/bin/bwrap \
        --ro-bind / / \
        --tmpfs /home \
        --tmpfs /media \
        --tmpfs /mnt \
        --tmpfs /tmp \
        -- "$MYDIR/$APP_START" "$@"
}


source "${0%/*}/setup-software.bash" "$@" app_settings
