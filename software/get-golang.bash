#!/usr/bin/env bash
#
# Golang 1.24.11 (Official) portable app
#

set -e


app_settings() {
    NAME="golang"
    VERSION="1.24.11"
    PORT="linux64-x86"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://go.dev/dl/go1.${VERSION#*.}.linux-amd64.tar.gz
    "
    APP_SHELL="
        mv go/* .
        rmdir go
    "
    APP_START="bin/go"
}

app_start() {
    MYDIR=$(realpath "${0%/*}")
    exec "$MYDIR/$APP_START" "$@"
}


source "${0%/*}/setup-software.bash" app_settings
