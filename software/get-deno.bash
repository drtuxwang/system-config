#!/usr/bin/env bash
#
# Deno 2.9.5 (Official) portable app
#

set -e


app_settings() {
    NAME="deno"
    VERSION="2.9.5"
    PORT="linux64-x86"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://github.com/denoland/deno/releases/download/v$VERSION/deno-x86_64-unknown-linux-gnu.zip
    "
}


source "${0%/*}/setup-software.bash" "$@" app_settings
