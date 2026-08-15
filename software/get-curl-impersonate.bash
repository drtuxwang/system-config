#!/usr/bin/env bash
#
# curl-impersonate 2.1.0 (Official) portable app
#

set -e


app_settings() {
    NAME="curl-impersonate"
    VERSION="2.1.0"
    PORT="linux64-x86"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://github.com/lexiforest/curl-impersonate/releases/download/v$VERSION/curl-impersonate-v$VERSION.x86_64-linux-gnu.tar.gz
    "
    APP_SHELL="
        cp -p curl-impersonate curl-impersonate.bin
        strip curl-impersonate.bin
        touch -r curl-impersonate curl-impersonate.bin
    "
    APP_START="curl-impersonate.bin"
    APP_LINK="curl-impersonate"
}

app_start() {
    MYDIR=$(realpath "${0%/*}")
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
