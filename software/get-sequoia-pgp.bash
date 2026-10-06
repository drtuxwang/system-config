#!/usr/bin/env bash
#
# Sequoia PGP 1.4.1 (Official) source code
#

set -e


app_settings() {
    NAME="sequoia-pgp"
    VERSION="1.4.1"
    PORT="source-rust"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://crates.io/api/v1/crates/sequoia-sq/$VERSION/download
        ${0%/*}/../compile/COMPILE-sequoia-pgp.bash
    "
    APP_SHELL="
        7z x -so download | tar xf -
        mv sequoia-sq-$VERSION/* .
    "
    APP_REMOVE="
        download
        sequoia-sq-$VERSION/
    "
}


source "${0%/*}/setup-software.bash" "$@" app_settings
