#!/usr/bin/env bash
#
# curl-impersonate 2.0.0 (Official) portable app
#

set -e


app_settings() {
    NAME="curl-impersonate"
    VERSION="2.0.0"
    PORT="linux64-x86"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://github.com/lexiforest/curl-impersonate/releases/download/v$VERSION/curl-impersonate-v$VERSION.x86_64-linux-gnu.tar.gz
    "
    APP_SHELL="
        cp -p curl-impersonate curl-impersonate.orig
        strip curl-impersonate
        touch -r curl-impersonate.orig curl-impersonate

        ln -s curl-sandbox curl-chrome
        ln -s curl-sandbox curl-firefox
    "
    APP_REMOVE="curl-impersonate.orig"
    APP_START="curl-impersonate"
    APP_LINK="curl-sandbox"
}

app_start() {
    MYDIR=$(realpath "${0%/*}")
    APP_START=$(ls -1 ${0%/*}/curl_${0##*-}[1-9][0-9][0-9] | tail -n -1)
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
